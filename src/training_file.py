from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from datasets import Dataset
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
import json
import torch
import os
from peft import LoraConfig, get_peft_model
from peft import PeftModel, PeftConfig
from training_data_extraction import process_telegram_data, process_zip_archive
from google_drive_connection import upload_files, authenticate
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

#gauth = GoogleAuth()
#gauth.LocalWebserverAuth()
#drive = GoogleDrive(gauth)

drive = authenticate()


def get_device():
    """
    Returns the device to be used for computations.

    Returns:
        str: The device to be used for computations. Possible values are "mps", "cuda", or "cpu".
    """
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def formatting_prompts_func(example):
    text = f"@@ПЕРВЫЙ@@ {example['previous_message']} @@ВТОРОЙ@@ {example['next_message']} @@ПЕРВЫЙ@@"
    return {"text": text}



def make_dataset_for_training(json_filename, count=-1): #old function
    with open(json_filename, "r", encoding="utf-8") as f:
        Vfile = json.load(f)

    dataset = [entry for entry in Vfile if isinstance(entry["previous_message"], str) and isinstance(entry["next_message"], str)]
    if count > 0:
        dataset = dataset[:count]
    dataset = Dataset.from_list(dataset)
    dataset = dataset.map(formatting_prompts_func)
    
    return dataset


def make_dataset_from_row_data(json_filename, username, count=-1):

    updated_dataset = process_zip_archive(json_filename, [], username)
    dataset = [entry for entry in updated_dataset if isinstance(entry["previous_message"], str) and isinstance(entry["next_message"], str)]
    if count > 0:
        dataset = dataset[:count]
    dataset = Dataset.from_list(dataset)
    dataset = dataset.map(formatting_prompts_func)
    
    return dataset


def train_model(zip_name, model_name, username, num_of_epochs=3, count=-1, drive=drive):
    """
    Trains a causal language model using the provided data in zip file and saves the model to output_dir.

    Args:
        zip_name (str): The name of the zip file containing the data.
        model_name (str): The directory where the trained model will be saved.(models/{model_name})
        username (str): The username on which we will train the model.
        num_of_epochs (int, optional): The number of epochs to train the model for. Defaults to 3.
        count (int, optional): The number of data entries to use for training. Defaults to -1 (use all entries).
        drive (str, optional): The drive on which we will upload the model (it will be later). Defaults to None(don't upload).

    Returns:
        None
    """
    
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    
    my_device = get_device()
    use_mps = False
    if my_device == "mps":
        use_mps = True
        os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
    print("\n\n", use_mps, "\n\n")
    dataset = make_dataset_from_row_data(zip_name, username, count=count)
    model = AutoModelForCausalLM.from_pretrained("tinkoff-ai/ruDialoGPT-medium").to(my_device)
    tokenizer = AutoTokenizer.from_pretrained("tinkoff-ai/ruDialoGPT-medium")
    target_modules = ['c_proj','c_attn', 'c_fc']

    config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, config)

    response_template = "@@ВТОРОЙ@@"
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)
    training_args = TrainingArguments(
        output_dir=f"models/{model_name}",
        logging_dir='./logs',            # Директория для логов
        per_device_train_batch_size=2,   # Размер батча на устройстве
        num_train_epochs=num_of_epochs,              # Количество эпох тренировки
        logging_steps=300,                # Частота логгирования
        save_total_limit=1,
        save_strategy="epoch",
        
    )
    trainer = SFTTrainer(
        model,
        train_dataset=dataset,
        args=training_args,
        dataset_text_field="text",
        data_collator=collator,
        peft_config=config,
        max_seq_length=1024,
    )
    print("\n\n")
    trainer.train()
    model.save_pretrained(f"models/{model_name}")
    

    if drive is not None:
        upload_files(drive, f"./models", model_name)


#train_model("datasets/ontyaga.json", "models/ontyaga_4ep", num_of_epochs=4)


#train_model('data/res.zip', 'Egopoler_low', 'Egopoler', num_of_epochs=1, count=100)

def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )

def finetune_model(zip_name, model_name, username, num_of_epochs=3, count=-1, drive=drive): #TODO
    """
    Trains a causal language model using the provided data in zip file and saves the model to output_dir.

    Args:
        zip_name (str): The name of the zip file containing the data.
        model_name (str): The directory where the trained model will be saved.(models/{model_name})
        username (str): The username on which we will train the model.
        num_of_epochs (int, optional): The number of epochs to train the model for. Defaults to 3.
        count (int, optional): The number of data entries to use for training. Defaults to -1 (use all entries).
        drive (str, optional): The drive on which we will upload the model (it will be later). Defaults to None(don't upload).

    Returns:
        None
    """
    
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    
    my_device = get_device()
    use_mps = False
    if my_device == "mps":
        use_mps = True
        os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
    print("\n\n", use_mps, "\n\n")
    dataset = make_dataset_from_row_data(zip_name, username, count=count)
    #model = AutoModelForCausalLM.from_pretrained("tinkoff-ai/ruDialoGPT-medium").to(my_device)
    #tokenizer = AutoTokenizer.from_pretrained("tinkoff-ai/ruDialoGPT-medium")
    config = PeftConfig.from_pretrained(f"models/{model_name}/checkpoint-50")
    model_without_peft = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, return_dict=True)
    tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

    # Load the Lora model
    model = PeftModel.from_pretrained(model_without_peft, f"models/{model_name}/checkpoint-50")
    
    target_modules = ['c_proj','c_attn', 'c_fc']
    
    # config = LoraConfig(
    #     r=16,
    #     lora_alpha=32,
    #     target_modules=target_modules,
    #     lora_dropout=0.05,
    #     bias="none",
    #     task_type="CAUSAL_LM"
    # )

    #model = get_peft_model(model, config)
    

    response_template = "@@ВТОРОЙ@@"
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)
    training_args = TrainingArguments(
        output_dir="output",
        logging_dir='./logs',            # Директория для логов
        per_device_train_batch_size=2,   # Размер батча на устройстве
        num_train_epochs=num_of_epochs,              # Количество эпох тренировки
        logging_steps=300,                # Частота логгирования
        
    )
    trainer = SFTTrainer(
        model,
        train_dataset=dataset,
        args=training_args,
        dataset_text_field="text",
        data_collator=collator,
        peft_config=config,
        max_seq_length=1024,
    )
    print("\n\n")
    trainer.train(resume_from_checkpoint=f"models/{model_name}/checkpoint-50")
    model.save_pretrained(f"models/{model_name}1")

    if drive is not None:
        upload_files(drive, f"./models", model_name)


#finetune_model('data/res.zip', 'Egopoler_low', 'Egopoler', num_of_epochs=1, count=100)
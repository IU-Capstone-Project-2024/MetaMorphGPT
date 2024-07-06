from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from datasets import Dataset
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
import json
import torch
import os
from peft import LoraConfig, get_peft_model 



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



def make_dataset_for_training(json_filename, count=-1):
    with open(json_filename, "r", encoding="utf-8") as f:
        Vfile = json.load(f)
    dataset = [entry for entry in Vfile if isinstance(entry["previous_message"], str) and isinstance(entry["next_message"], str)]
    if count > 0:
        dataset = dataset[:count]
    dataset = Dataset.from_list(dataset)
    dataset = dataset.map(formatting_prompts_func)
    
    return dataset




def train_model(json_filename, output_dir, num_of_epochs=3, count=-1):
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    
    my_device = get_device()
    use_mps = False
    if my_device == "mps":
        use_mps = True
        os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
    print("\n\n", use_mps, "\n\n")
    dataset = make_dataset_for_training(json_filename, count=count)
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
    trainer.train()
    model.save_pretrained(output_dir)


train_model("datasets/andrey_dataset.json", "models/andrey_model_low", count=1000)
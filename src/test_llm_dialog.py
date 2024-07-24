from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig


default_model_path = 'models/0000'
# Функция для генерации ответа от модели
def generate_response(prompt, model, tokenizer):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(
    inputs,
    top_k=10,
    top_p=0.95,
    num_beams=3,
    num_return_sequences=3,
    do_sample=True,
    no_repeat_ngram_size=2,
    temperature=1.2,
    repetition_penalty=1.3,
    length_penalty=1.0,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=50257,
    max_new_tokens=40
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response




def get_answer1(history, user_input, model, tokenizer):

    if history == "":
        history = "@@ПЕРВЫЙ@@ "
    
    new_history = history + str(user_input + " @@ВТОРОЙ@@")

    response_starts = len(new_history)

    response = generate_response(new_history)
    
    only_response = response[response_starts:].replace("@@ВТОРОЙ@@", "").replace("@@ПЕРВЫЙ@@", "")
    
    new_history = " " + only_response + " @@ПЕРВЫЙ@@ "

    return only_response, new_history


def get_answer(history, user_input, model_path=default_model_path):

    config = PeftConfig.from_pretrained(model_path)
    model_without_peft = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, return_dict=True)
    tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

    # Load the Lora model
    model = PeftModel.from_pretrained(model_without_peft, model_path)

    if history == "":
        history = "@@ПЕРВЫЙ@@ "
    
    new_history = history + str(user_input + " @@ВТОРОЙ@@")

    response_starts = len(new_history)

    response = generate_response(new_history, model, tokenizer)
    
    only_response = response[response_starts:].replace("@@ВТОРОЙ@@", "").replace("@@ПЕРВЫЙ@@", "")
    
    new_history += " " + only_response + " @@ПЕРВЫЙ@@ "

    return only_response, new_history

def start_local_chat():
    # Основной цикл для общения с моделью
    print("Начните общение с моделью (введите 'exit' для выхода)")

    history = ""
    while True:
        user_input = input("Вы: ")
        if user_input.lower() == "exit":
            break
        
        answer, history = get_answer(history, user_input, default_model_path)

        print("Модель: " + answer)


#start_local_chat()
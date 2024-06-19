from transformers import AutoModelForCausalLM, AutoTokenizer


# Загрузка модели и токенизатора
model_name = "tinkoff-ai/ruDialoGPT-small"
model_name_1 = 'tinkoff-ai/ruDialoGPT-medium'
tokenizer = AutoTokenizer.from_pretrained(model_name_1)
model = AutoModelForCausalLM.from_pretrained(model_name_1)

# Функция для генерации ответа от модели
def generate_response(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    #outputs = model.generate(inputs, max_length=100, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id, repetition_penalty=1.3)
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

# Основной цикл для общения с моделью
print("Начните общение с моделью (введите 'exit' для выхода)")

print(tokenizer.bos_token)
history = "@@ПЕРВЫЙ@@ "
while True:
    user_input = input("Вы: ")
    if user_input.lower() == "exit":
        break
    history += str(user_input + " @@ВТОРОЙ@@")
    response = generate_response(history)
    response_starts = len(history)
    
    #print("Модель: " + response) 
    # раскомментить только для теста
    
    
    only_response = response[response_starts:].replace("@@ВТОРОЙ@@", "").replace("@@ПЕРВЫЙ@@", "")
    print("Обрезанная часть: " + only_response)

    # Добавляем ответ в историю

    history += " " + only_response + " @@ПЕРВЫЙ@@ "
    
from transformers import T5ForConditionalGeneration, T5Tokenizer

model_path = "scripts\\YAP\\my_finetuned_model"
model = T5ForConditionalGeneration.from_pretrained(model_path)
tokenizer = T5Tokenizer.from_pretrained(model_path)

input_file_path = "C:\\Users\\sheny\\Downloads\\про\\Пример.txt"
with open(input_file_path, "r", encoding="utf-8") as file:
    input_text = file.read()
input_ids = tokenizer.encode(input_text, return_tensors="pt") 
# Установите параметры генерации по вашему усмотрению
output_sequences = model.generate(
    input_ids=input_ids,
    max_length=50,  # Максимальная длина выходной последовательности
    num_beams=5,    # Использование beam search с указанным количеством лучей
    temperature=1.0,  # Температура для управления случайностью выходных данных
    no_repeat_ngram_size=2  # Предотвращение повторения n-грамм в выходных данных
)
output_text = tokenizer.decode(output_sequences[0], skip_special_tokens=True)
print(output_text)
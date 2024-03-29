from transformers import T5Tokenizer, T5ForConditionalGeneration, get_linear_schedule_with_warmup
import torch
import glob
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from torch.optim import AdamW

tokenizer = AutoTokenizer.from_pretrained("ai-forever/ruT5-base", legacy=False)
model = AutoModelForSeq2SeqLM.from_pretrained("ai-forever/ruT5-base")
num_epochs = 10
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()


class TextDataset(Dataset):
    def __init__(self, tokenizer, input_texts, output_texts):
        self.tokenizer = tokenizer
        self.input_texts = input_texts
        self.output_texts = output_texts

    def __len__(self):
        return len(self.input_texts)

    def __getitem__(self, idx):
        input_text = self.input_texts[idx]
        output_text = self.output_texts[idx]
        
        # Токенизация текста
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids.squeeze()
        labels = self.tokenizer(output_text, return_tensors="pt").input_ids.squeeze()
        
        return {
            "input_ids": input_ids,
            "labels": labels
        }


input_file_path = glob.glob("C:\\Users\\sheny\\Downloads\\про\\input*.txt")
output_file_path = glob.glob("C:\\Users\\sheny\\Downloads\\про\\output*.txt")

input_file_path.sort()
output_file_path.sort()

input_texts = [read_file(file_path) for file_path in input_file_path]
output_texts = [read_file(file_path) for file_path in output_file_path]

train_dataset = TextDataset(tokenizer, input_texts, output_texts)

train_dataloader = DataLoader(train_dataset, batch_size=8, shuffle=True)

optimizer = AdamW(model.parameters(), lr=5e-5)
num_training_steps = len(train_dataloader) * num_epochs
lr_scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

for epoch in range(num_epochs):
    model.train()
    for batch in train_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        
        input_ids = batch['input_ids']
        labels = batch['labels']
        
        # Обратите внимание, что model.forward теперь принимает параметры явно
        outputs = model(input_ids=input_ids, labels=labels)
        loss = outputs.loss
        loss.backward()

        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        print(f"Epoch: {epoch}, Loss: {loss.item()}")
model.save_pretrained('scripts\\YAP\\my_finetuned_model')
tokenizer.save_pretrained('scripts\\YAP\\my_finetuned_model')


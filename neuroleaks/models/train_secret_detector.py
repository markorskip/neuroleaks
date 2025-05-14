import os
import random
import torch
from datasets import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
)

# === CONFIG ===
MODEL_NAME = "bert-base-uncased"
SAVE_DIR = "./models/secret-detector"
EPOCHS = 3
BATCH_SIZE = 8
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

# === SYNTHETIC DATA GENERATION ===


dataset = load_from_disk("secret_detection_dataset")

# === TOKENIZATION ===
def tokenize(example):
    return tokenizer(example["text"], padding="max_length", truncation=True, max_length=128)

# === MAIN TRAINING FUNCTION ===
def main():
    print("🚀 Generating synthetic data...")
    dataset = generate_synthetic_data(1000)
    dataset = dataset.train_test_split(test_size=0.2)

    global tokenizer
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    tokenized_dataset = dataset.map(tokenize, batched=True)
    tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

    print("🧠 Initializing model...")
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    training_args = TrainingArguments(
        output_dir=SAVE_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=10,
        seed=SEED,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
    )

    print("🏋️ Training model...")
    trainer.train()

    print("💾 Saving model to:", SAVE_DIR)
    trainer.save_model(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)
    print("✅ Done!")

if __name__ == "__main__":
    main()

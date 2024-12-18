import pandas as pd
import os
import torch
from transformers import BertForSequenceClassification, BertTokenizer

# Function to preprocess and tokenize email body for BERT and RoBERTa models
def tokenize_email_body(email_body, text_tokenizer, max_length=512):
    text_inputs = text_tokenizer(email_body, return_tensors='pt', max_length=max_length, truncation=True, padding=True)
    return text_inputs

class TextClassifier:
    def __init__(self):
        output_dir = "../PhishingDetectionModel/TextAnalysis/results/bert_lr_2e-5_bs_16_epochs_4"
        checkpoints = [f.path for f in os.scandir(output_dir) if f.is_dir() and 'checkpoint' in f.name]
        latest_checkpoint = max(checkpoints, key=os.path.getmtime)  # Gets the most recent checkpoint based on modification time

        # Load the best model (the one automatically saved at the end of training)
        self.text_model = BertForSequenceClassification.from_pretrained(latest_checkpoint)
        self.text_tokenizer = BertTokenizer.from_pretrained(latest_checkpoint)

    def predict(self, email_text):
        # If email_text is a pandas Series, extract the string from it
        if isinstance(email_text, pd.Series):
            email_text = email_text.iloc[0]  # Extract the first element of the Series

        text_inputs = tokenize_email_body(email_text, self.text_tokenizer)
        with torch.no_grad():
            text_output = self.text_model(**text_inputs)
            text_predictions = torch.softmax(text_output.logits, dim=-1).numpy()

        return text_predictions
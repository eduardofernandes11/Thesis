import torch
import torch.nn.functional as F  # For applying softmax
from transformers import RobertaModel, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

# Optional: Define a helper function for preprocessing if you like
def preprocess_email(email_text, tokenizer):
    inputs = tokenizer(email_text, padding=True, truncation=True, return_tensors='pt')
    return inputs

class EmotionClassifier:
    def __init__(self):
        self.model_name = 'SamLowe/roberta-base-go_emotions'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def _load_model(self):
        # Load the saved state_dict
        state_dict = torch.load('../PhishingDetectionModel/EmotionAnalysis/Models/14_emotion_reddit_roberta/4e-05_roberta_model_epoch_8.pth', map_location=torch.device('cpu'))

        # Remove the 'model.' prefix from all keys in the state_dict
        new_state_dict = {}
        for key in state_dict.keys():
            new_key = key.replace('model.', '')  # Remove 'model.' prefix
            new_state_dict[new_key] = state_dict[key]

        # Load the modified state_dict into your model
        emotion_model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=14, ignore_mismatched_sizes=True)
        emotion_model.load_state_dict(new_state_dict)
        # model = RobertaEmotionsClass("SamLowe/roberta-base-go_emotions")
        # model.load_state_dict(torch.load('../EmotionAnalysis/pytorch_roberta_emotion_email.bin'))
        return emotion_model

    def predict(self, email_text):
        # If email_text is a pandas Series, extract the string from it
        if isinstance(email_text, pd.Series):
            email_text = email_text.iloc[0]  # Extract the first element of the Series

        if not hasattr(self, 'model'):
            self.model = self._load_model()

        inputs = preprocess_email(email_text, self.tokenizer)

        # Make sure the model is on CPU
        self.model.to(torch.device('cpu'))

        self.model.eval()   
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Extract logits
        logits = outputs.logits

        # Get the predicted emotion (the index with the highest logit)
        emotion_index = logits.argmax(dim=-1).item()

        # Apply softmax to the logits to get probabilities (confidence scores)
        probabilities = F.softmax(logits, dim=-1)

        # Get the confidence score of the predicted emotion
        confidence_score = probabilities[0, emotion_index].item()

        return emotion_index, confidence_score

import torch
from transformers import RobertaModel, RobertaTokenizer, AutoModelForSequenceClassification
from model_classes.roberta_emotions import RobertaEmotionsClass

# Optional: Define a helper function for preprocessing if you like
def preprocess_email(email_text, tokenizer):
    inputs = tokenizer(email_text, padding=True, truncation=True, return_tensors='pt')
    return inputs

class EmotionClassifier:
    def __init__(self):
        self.tokenizer = RobertaTokenizer.from_pretrained('../EmotionAnalysis/')

    def _load_model(self):
        model = RobertaEmotionsClass("SamLowe/roberta-base-go_emotions")
        model.load_state_dict(torch.load('../EmotionAnalysis/pytorch_roberta_emotion_email.bin'))
        return model

    def predict(self, email_text):
        if not hasattr(self, 'model'):
            self.model = self._load_model()

        inputs = preprocess_email(email_text, self.tokenizer)

        self.model.eval()   
        with torch.no_grad():
            outputs = self.model(**inputs)

        print(outputs)
        # Replace this with your logic to get the actual emotion label from outputs
        # predicted_emotion = extract_emotion(outputs) 
        return outputs 

import torch
import joblib
from transformers import RobertaModel, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class HeadersClassifier:
    def __init__(self):
        self.header_model = joblib.load('../PhishingDetectionModel/MetadataAnalysis/models/best_model_gb.pkl')  # Model trained on email headers

    def predict(self, email_headers):
        headers_predictions = self.header_model.predict_proba(email_headers)

        print(headers_predictions)

        return headers_predictions 

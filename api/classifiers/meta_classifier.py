import torch
import joblib
from transformers import RobertaModel, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class MetaClassifier:
    def __init__(self):
        self.meta_model = joblib.load('../PhishingDetectionModel/MetaModel/results/rf_meta_model.pkl')  # Model trained on email headers

    def predict(self, models_outputs):
        meta_predictions = self.meta_model.predict_proba(models_outputs)

        print(meta_predictions)

        return meta_predictions 
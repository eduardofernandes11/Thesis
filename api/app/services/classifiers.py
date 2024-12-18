from classifiers.headers_classifier import HeadersClassifier
from classifiers.text_classifier import TextClassifier
from classifiers.emotion_classifier import EmotionClassifier
from classifiers.meta_classifier import MetaClassifier
from app.utils.mapping import emotion_mapping
from app.db import results_db
import numpy as np

# Initialize classifiers
headers_classifier = HeadersClassifier()
text_classifier = TextClassifier()
emotion_classifier = EmotionClassifier()
meta_classifier = MetaClassifier()

# Analyze headers
def headers_analysis(email_headers, job_id):
    headers_prediction = headers_classifier.predict(email_headers.to_numpy())
    results_db[job_id] = {"job_id": job_id, "is_phishing": bool(headers_prediction.argmax()), "emotions": {}}
    return headers_prediction.argmax()

# Analyze text
def text_analysis(email_text, job_id):
    text_prediction = text_classifier.predict(email_text)
    results_db[job_id]["is_phishing"] = bool(text_prediction.argmax())
    return text_prediction.argmax()

# Analyze emotion
def emotion_analysis(email_text, job_id):
    emotion_prediction, emotion_confidence = emotion_classifier.predict(email_text)
    # Get the emotion prediction string value
    emotion_label = [key for key, value in emotion_mapping.items() if value == emotion_prediction][0]

    # Update the results database with the prediction
    results_db[job_id]["emotions"].update({
        emotion_label: emotion_confidence
    })
    return emotion_prediction, emotion_confidence

# Combine all classifiers
def ensemble_analysis(email_headers, email_text, job_id):
    headers_prediction = headers_analysis(email_headers, job_id)
    text_prediction = text_analysis(email_text, job_id)
    emotion_prediction, emotion_confidence = emotion_analysis(email_text, job_id)

    # Reshape predictions to be a 2D array
    models_outputs = [headers_prediction, text_prediction, emotion_prediction]
    models_outputs = np.array(models_outputs).reshape(1, -1)  # Reshape to 2D

    # Get the meta classifier prediction
    meta_predictions = meta_classifier.predict(models_outputs)

    # Get the emotion prediction string value
    emotion_label = [key for key, value in emotion_mapping.items() if value == emotion_prediction][0]

    # Update the results database with the meta classifier prediction
    results_db[job_id] = {"job_id": job_id, "is_phishing": bool(meta_predictions.argmax()), "emotions": {emotion_label: emotion_confidence}}

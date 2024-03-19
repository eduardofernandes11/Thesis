from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from classifiers.emotion_classifier import EmotionClassifier
import uuid

app = FastAPI()

class AnalysisResult(BaseModel):
    job_id: str
    is_phishing: Optional[bool] = None
    emotions: Optional[dict] = None

emotion_classifier = EmotionClassifier()

# Simulated in-memory database for job results
results_db = {}

# Define a function to process the email, which will be run in the background
def process_email(file_path: str, job_id: str):
    # Placeholder for actual processing logic:
    # You would integrate your models here to process the email.
    # For example, analyzing metadata, text preprocessing, and emotion classification.

    # Read the .eml file content
    with open(file_path, 'r') as file:
        email_content = file.read()

    predicted_emotion = emotion_classifier.predict(email_content)

    print(f"Predicted Emotion: {predicted_emotion}") 

    # After processing, store the result
    results_db[job_id] = {
        "is_phishing": True,  # Example result
        "emotions": {"fear": 0.9}  # Example result
    }

@app.post("/receive_email", response_model=AnalysisResult)
async def receive_email(background_tasks: BackgroundTasks, email_file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    results_db[job_id] = None  # Initialize the result entry

    # Save the file temporarily
    file_location = f"/tmp/{job_id}.eml"
    with open(file_location, "wb+") as file_object:
        file_object.write(email_file.file.read())

    # Add the processing task to the background
    background_tasks.add_task(process_email, file_location, job_id)

    return {"job_id": job_id}

@app.get("/results/{job_id}", response_model=AnalysisResult)
async def get_results(job_id: str):
    if job_id not in results_db:
        raise HTTPException(status_code=404, detail="Job ID not found")
    if results_db[job_id] is None:
        return {"job_id": job_id}  # Processing is still ongoing
    return results_db[job_id]

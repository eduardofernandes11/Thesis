from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from app.services.classifiers import headers_analysis, text_analysis, emotion_analysis
from app.models.schemas import AnalysisResult
from app.services.process_email import process_email
from app.db import email_db, results_db
import uuid

router = APIRouter()

@router.post("/analyze-headers")
async def analyze_headers(background_tasks: BackgroundTasks, email_file: UploadFile = File(...), user_email: str = None):
    job_id = str(uuid.uuid4())
    results_db[job_id] = None  # Initialize the result entry

    # Get the name of the email file
    email_filename = email_file.filename

    # Save the file temporarily
    file_location = f"/tmp/{job_id}.eml"
    with open(file_location, "wb+") as file_object:
        file_object.write(email_file.file.read())

    # Preprocess the email
    process_email(file_location, job_id, user_email, email_filename)

    # Add the headers analysis task to the background
    headers_analysis(email_db[job_id]["email_headers"], job_id)

    return results_db[job_id]

@router.get("/analyze-text")
async def analyze_text(background_tasks: BackgroundTasks, job_id: str):

    # Add the processing task to the background
    text_analysis(email_db[job_id]['email_body'], job_id)

    return results_db[job_id]

@router.get("/analyze-emotion")
async def analyze_emotion(background_tasks: BackgroundTasks, job_id: str):

    # Add the processing task to the background
    emotion_analysis(email_db[job_id]['email_body'], job_id)

    return results_db[job_id]
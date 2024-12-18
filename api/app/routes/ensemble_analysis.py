from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from app.services.classifiers import headers_analysis, text_analysis, emotion_analysis, ensemble_analysis
from app.models.schemas import AnalysisResult
from app.services.process_email import process_email
from app.db import email_db, results_db
import uuid

router = APIRouter()

@router.post("/analyze-email")
async def analyze_email(background_tasks: BackgroundTasks, email_file: UploadFile = File(...), user_email: str = None):
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

    # Get ensemble analysis results
    ensemble_analysis(email_db[job_id]["email_headers"], email_db[job_id]["email_body"], job_id)

    return results_db[job_id]
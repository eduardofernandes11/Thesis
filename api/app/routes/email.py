from fastapi import APIRouter, HTTPException
from app.services.email_sender import send_results_email, forward_email, send_results_email_csirt
from app.models.schemas import AnalysisResult
from app.db import email_db, results_db

router = APIRouter()

@router.post("/send-results")
async def send_results(job_id: str):
    print(results_db)
    if job_id not in results_db or job_id not in email_db:
        raise HTTPException(status_code=404, detail="Job ID not found")
    if results_db[job_id] is None:
        raise HTTPException(status_code=400, detail="Results are not ready yet")

    # Call the email sender service
    send_results_email(job_id)

    return {"message": "Email sent successfully"}

@router.post("/send-results-csirt")
async def send_results_csirt(job_id: str):
    print(results_db)
    if job_id not in results_db or job_id not in email_db:
        raise HTTPException(status_code=404, detail="Job ID not found")
    if results_db[job_id] is None:
        raise HTTPException(status_code=400, detail="Results are not ready yet")

    # Call the email sender service
    send_results_email_csirt(job_id)

    return {"message": "Email sent successfully"}

@router.post("/forward-email")
async def forward_email_route():
    try:
        return await forward_email()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/results/{job_id}", response_model=AnalysisResult)
async def get_results(job_id: str):
    if job_id not in results_db:
        raise HTTPException(status_code=404, detail="Job ID not found")
    if results_db[job_id] is None:
        return {"job_id": job_id}  # Processing is still ongoing
    return results_db[job_id]

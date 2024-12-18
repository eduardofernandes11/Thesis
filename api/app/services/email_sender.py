from http.client import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.db import email_db, results_db
import os
import httpx

def send_results_email(job_id: str):
    # Email parameters
    sender_email = "rezetrl@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "rezetrl@gmail.com"
    smtp_password = "kicw hvbd hdlk lzpf"

    # Fetch results
    results = results_db[job_id]

    # Get the recipient email from the email database
    recipient_email = email_db[job_id]["user_email"]
    email_filename = email_db[job_id]["email_filename"]

    # Compose the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Analysis Results for Email file '{email_filename}' with Job ID {job_id}"

    email_content = f"""
        Job ID: {job_id}
        Is Phishing: {results['is_phishing']}
        """

    message.attach(MIMEText(email_content, "plain"))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
def send_results_email_csirt(job_id: str):
    # Email parameters
    sender_email = "rezetrl@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "rezetrl@gmail.com"
    smtp_password = "kicw hvbd hdlk lzpf"

    # Fetch results
    results = results_db[job_id]

    # Get the recipient email from the email database
    recipient_email = email_db[job_id]["user_email"]
    email_filename = email_db[job_id]["email_filename"]

    # Compose the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"CSIRT Analysis Results for Email file '{email_filename}' with Job ID {job_id}"

    email_content = f"""
        Job ID: {job_id}
        Is Phishing: {results['is_phishing']}
        Emotions: {results['emotions']}
        """

    message.attach(MIMEText(email_content, "plain"))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

async def forward_email():
    phishing_file_path = '../Data/PhishingPotEmls/phishing.eml'
    safe_file_path = '../Data/trec07p/data/inmail.2'
    file_path = safe_file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # The target URL of the external API where the file will be sent
    target_url = "http://localhost:5678/webhook/send-email?user_email=eduardofernandes@ua.pt"
    with open(file_path, "rb") as eml_file:
        # Using httpx to send the file as multipart/form-data
        files = {'email_file': (os.path.basename(file_path), eml_file, 'message/rfc822')}

        async with httpx.AsyncClient() as client:
            response = await client.post(target_url, files=files)

        # Check if the response is successful
        if response.status_code == 200:
            return {"message": "File successfully forwarded", "response": response.json()}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to forward the file. Status code: {response.status_code}"
            )
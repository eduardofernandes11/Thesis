from pydantic import BaseModel
from typing import Optional

class AnalysisResult(BaseModel):
    job_id: str
    is_phishing: Optional[bool] = None
    emotions: Optional[dict] = None

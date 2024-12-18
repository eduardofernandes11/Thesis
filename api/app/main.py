from fastapi import FastAPI
from app.routes import bpmn_analysis, email, ensemble_analysis

app = FastAPI()

# Include the routers
app.include_router(bpmn_analysis.router, prefix="/stepwise-analysis", tags=["stepwise-analysis"])
app.include_router(ensemble_analysis.router, prefix="/ensemble-analysis", tags=["ensemble-analysis"])
app.include_router(email.router, prefix="/email", tags=["email"])
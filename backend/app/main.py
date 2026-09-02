import uuid
from fastapi import FastAPI
from backend.app.models.schemas import ReportRequest
from backend.app.services.db_service import create_report_entry, get_report_by_id

app = FastAPI()


@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/generate-report")
def generate_report(request: ReportRequest):
    user_id = str(uuid.uuid4()) 
    report = create_report_entry(topic = request.topic, user_id = user_id,)
    
    return report
       

@app.get("/report/{report_id}")
def get_report(report_id: int):
    report = get_report_by_id(report_id)
    return report
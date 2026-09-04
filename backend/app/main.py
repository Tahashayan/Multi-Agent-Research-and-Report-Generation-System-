import uuid
from fastapi import FastAPI, HTTPException
from backend.app.models.schemas import ReportRequest
from backend.app.services.db_service import create_report_entry, get_report_by_id, update_report_content, update_report_status_failed
from backend.app.agents.graph import run_research_graph

app = FastAPI()


@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/generate-report")
def generate_report(request: ReportRequest):
    user_id = str(uuid.uuid4()) 
    report = create_report_entry(topic = request.topic, user_id = user_id)
    try:
        final_report = run_research_graph(topic = request.topic)
        dict_content = final_report.model_dump()
        updated_report = update_report_content(
            report["id"],
            dict_content,
        )
    except Exception as e:
        update_report_status_failed(report["id"])

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    
    return updated_report
       

@app.get("/report/{report_id}")
def get_report(report_id: int):
    report = get_report_by_id(report_id)
    return report
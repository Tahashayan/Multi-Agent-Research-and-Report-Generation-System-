import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from backend.app.models.schemas import ReportRequest
from backend.app.services.db_service import create_report_entry, get_report_by_id, update_report_content, update_report_status_failed
from backend.app.agents.graph import run_research_graph

app = FastAPI()


@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/generate-report")
async def generate_report(request: ReportRequest, background_task: BackgroundTasks):
    user_id = str(uuid.uuid4()) 
    report = create_report_entry(topic = request.topic, user_id = user_id)
    background_task.add_task(process_report_in_background, report["id"], request.topic)
    return report
    
@app.get("/report/{report_id}")
def get_report(report_id: str):
    report = get_report_by_id(report_id)
    return report


async def process_report_in_background(report_id: str, topic: str):
    try:
        final_report = run_research_graph(topic)
        dict_content = final_report.model_dump()
        update_report_content(
            report_id,
            dict_content,
        )
    except Exception as e:
        update_report_status_failed(report_id)
        print(f"Task failed: {e}")
        

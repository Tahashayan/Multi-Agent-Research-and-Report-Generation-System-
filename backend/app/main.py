import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from backend.app.models.schemas import ReportRequest
from backend.app.services.db_service import create_report_entry, get_report_by_id, update_report_content, update_report_status_failed, update_report_status_pending_approval
from backend.app.agents.graph import run_research_graph, resume_research_graph

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

@app.post("/approve-report/{report_id}")
async def approve_report(report_id: str, background_task: BackgroundTasks):
    background_task.add_task(process_report_approval_in_background, report_id)
    return {"status": "Report approved"}
    
@app.get("/report/{report_id}")
def get_report(report_id: str):
    report = get_report_by_id(report_id)
    return report


async def process_report_in_background(report_id: str, topic: str):
    try:
        final_report = run_research_graph(report_id, topic)
        if final_report == "pending_approval":
            update_report_status_pending_approval(report_id)
            print(f"⏸️  Report {report_id} awaiting human approval, exiting worker.")
            return
        dict_content = final_report.model_dump() if hasattr(final_report, "model_dump") else final_report
        update_report_content(
            report_id,
            dict_content,
        )
    except Exception as e:
        update_report_status_failed(report_id)
        print(f"Task failed: {e}")
        
async def process_report_approval_in_background(report_id: str):
    try:
        final_report = resume_research_graph(report_id)
        
        update_report_content(
            report_id,
            final_report,
        )
    except Exception as e:
        update_report_status_failed(report_id)
        print(f"Task failed: {e}")
        

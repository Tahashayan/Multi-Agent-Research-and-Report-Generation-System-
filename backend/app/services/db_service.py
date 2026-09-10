from supabase import Client, create_client

from backend.app.core.config import config

supabase: Client = create_client(
    config.supabase_url,
    config.supabase_key,
)


def create_report_entry(topic: str, user_id: str):
    response = (
        supabase
        .table("reports")
        .insert({
            "topic": topic,
            "user_id": user_id,
            "status": "pending",
        })
        .execute()
    )

    return response.data[0] if response.data else None


def get_report_by_id(report_id: str):
    response = (
        supabase
        .table("reports")
        .select("*")
        .eq("id", report_id)
        .single()
        .execute()
    )

    return response.data


def update_report_content(report_id: str, content: dict):
    response = (
        supabase
        .table("reports")
        .update({"status": "completed", "content": content})
        .eq("id", report_id)
        .execute()
    )
    
    return response.data[0] if response.data else None

def update_report_status_failed(report_id: str):
    response = (
        supabase
        .table("reports")
        .update({"status": "failed"})
        .eq("id", report_id)
        .execute()
    )
    return response.data[0] if response.data else None

def update_report_step(report_id: str, step_message: str):
    response = (
        supabase
        .table("reports")
        .update({"current_step": step_message})
        .eq("id", report_id)
        .execute()
    )
    return response.data[0] if response.data else None

def update_report_status_pending_approval(report_id: str):
    response = (
        supabase
        .table("reports")
        .update({"status": "pending_approval"})
        .eq("id", report_id)
        .execute()
    )
    return response.data[0] if response.data else None
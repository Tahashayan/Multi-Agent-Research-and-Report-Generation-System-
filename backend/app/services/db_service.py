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


def get_report_by_id(report_id: int):
    response = (
        supabase
        .table("reports")
        .select("*")
        .eq("id", report_id)
        .single()
        .execute()
    )

    return response.data
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    topic: str


class ReportResponse(BaseModel):
    id: int
    user_id: str
    topic: str
    status: str
    content: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    

class FinalReport(BaseModel):
    title: str
    executive_summary: str
    key_data_points: list[str]
    conclusion: str
    
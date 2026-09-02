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
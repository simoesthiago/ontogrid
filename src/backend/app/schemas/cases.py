from datetime import datetime

from pydantic import BaseModel


class CaseCreate(BaseModel):
    asset_id: str
    alert_id: str | None = None
    title: str
    priority: str = "medium"


class CaseResponse(BaseModel):
    id: str
    asset_id: str
    alert_id: str | None = None
    title: str
    status: str
    priority: str
    created_at: datetime


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    total: int

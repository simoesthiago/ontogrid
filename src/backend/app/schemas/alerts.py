from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    asset_id: str
    severity: str
    status: str
    alert_type: str
    message: str
    created_at: datetime
    acknowledged_at: datetime | None = None


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int


class AlertAckResponse(BaseModel):
    id: str
    status: str
    acknowledged_at: datetime | None = None

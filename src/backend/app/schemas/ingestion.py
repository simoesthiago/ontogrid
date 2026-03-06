from datetime import datetime

from pydantic import BaseModel


class MeasurementRecord(BaseModel):
    asset_id: str
    measurement_type: str
    value: float
    timestamp: datetime
    quality_flag: str = "good"
    source: str = "api"


class JsonBatchJobRequest(BaseModel):
    source_type: str = "json_batch"
    payload_format: str = "json"
    records: list[MeasurementRecord]


class IngestionJobResponse(BaseModel):
    id: str
    status: str
    source_type: str
    payload_format: str
    records_received: int
    records_accepted: int
    records_rejected: int
    error_summary: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

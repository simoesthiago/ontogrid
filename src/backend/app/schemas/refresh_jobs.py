from pydantic import BaseModel


class RefreshJobItem(BaseModel):
    id: str
    dataset_id: str
    dataset_code: str
    dataset_name: str
    source_code: str
    trigger_type: str
    status: str
    rows_read: int
    rows_written: int
    error_summary: str | None
    created_at: str
    started_at: str | None
    finished_at: str | None
    published_version_id: str | None
    published_version_label: str | None


class RefreshJobListResponse(BaseModel):
    items: list[RefreshJobItem]
    total: int

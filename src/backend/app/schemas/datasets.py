from pydantic import BaseModel


class DatasetListItem(BaseModel):
    id: str
    source_code: str
    code: str
    name: str
    domain: str
    granularity: str
    latest_version: str
    latest_published_at: str
    freshness_status: str


class DatasetListResponse(BaseModel):
    items: list[DatasetListItem]
    total: int


class DatasetVersionSummary(BaseModel):
    id: str
    label: str
    published_at: str


class DatasetDetailResponse(BaseModel):
    id: str
    source_id: str
    source_code: str
    code: str
    name: str
    domain: str
    description: str
    granularity: str
    refresh_frequency: str
    schema_summary: dict[str, list[str]]
    latest_version: DatasetVersionSummary


class DatasetVersionItem(BaseModel):
    id: str
    label: str
    extracted_at: str
    published_at: str
    coverage_start: str
    coverage_end: str
    status: str
    checksum: str


class DatasetVersionListResponse(BaseModel):
    dataset_id: str
    items: list[DatasetVersionItem]


class DatasetVersionDetailResponse(BaseModel):
    id: str
    dataset_id: str
    label: str
    extracted_at: str
    published_at: str
    coverage_start: str
    coverage_end: str
    row_count: int
    schema_version: str
    checksum: str
    lineage: dict[str, str]


class DatasetRefreshResponse(BaseModel):
    refresh_job_id: str
    dataset_id: str
    status: str
    requested_at: str

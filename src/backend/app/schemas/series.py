from pydantic import BaseModel


class SeriesListItem(BaseModel):
    id: str
    dataset_id: str
    metric_code: str
    metric_name: str
    unit: str
    temporal_granularity: str
    entity_type: str
    latest_observation_at: str


class SeriesListResponse(BaseModel):
    items: list[SeriesListItem]
    total: int


class ObservationItem(BaseModel):
    timestamp: str
    value: float
    unit: str
    quality_flag: str
    published_at: str


class ObservationListResponse(BaseModel):
    series_id: str
    dataset_version_id: str
    items: list[ObservationItem]

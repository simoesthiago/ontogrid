from pydantic import BaseModel


class InsightCard(BaseModel):
    id: str
    title: str
    value: float
    unit: str
    trend: str


class InsightHighlight(BaseModel):
    title: str
    dataset_version_id: str


class InsightOverviewResponse(BaseModel):
    cards: list[InsightCard]
    highlights: list[InsightHighlight]


class EntityInsightSeries(BaseModel):
    series_id: str
    metric_code: str


class EntityInsightChange(BaseModel):
    dataset_version_id: str
    message: str


class EntityInsightResponse(BaseModel):
    entity_id: str
    summary: str
    related_series: list[EntityInsightSeries]
    recent_changes: list[EntityInsightChange]

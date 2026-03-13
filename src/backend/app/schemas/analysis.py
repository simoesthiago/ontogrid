from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


VisualizationType = Literal["table", "bar", "column", "line", "pie"]
AggregationType = Literal["sum", "avg", "count", "min", "max"]


class AnalysisFilter(BaseModel):
    field: str
    operator: Literal["in"]
    values: list[str] = Field(default_factory=list)


class AnalysisMeasure(BaseModel):
    field: str
    aggregation: AggregationType


class AnalysisVisualization(BaseModel):
    type: VisualizationType = "table"


class AnalysisViewConfig(BaseModel):
    dataset_id: str
    entity_id: str | None = None
    rows: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    filters: list[AnalysisFilter] = Field(default_factory=list)
    measures: list[AnalysisMeasure] = Field(default_factory=list)
    visualization: AnalysisVisualization = Field(default_factory=AnalysisVisualization)


class AnalysisFieldItem(BaseModel):
    id: str
    label: str
    kind: Literal["entity", "time", "dimension"]


class AnalysisMetricItem(BaseModel):
    field: str
    label: str
    unit: str
    supported_aggregations: list[AggregationType]


class AnalysisFieldsResponse(BaseModel):
    dataset_id: str
    dimensions: list[AnalysisFieldItem]
    metrics: list[AnalysisMetricItem]
    time_fields: list[str]
    entity_field: str | None = None
    default_measure: str | None = None


class AnalysisQueryRequest(BaseModel):
    config: AnalysisViewConfig


class AnalysisQueryColumn(BaseModel):
    id: str
    label: str
    kind: Literal["dimension", "measure"]


class AnalysisQueryRow(BaseModel):
    values: dict[str, object | None]


class AnalysisQueryResponse(BaseModel):
    dataset_id: str
    columns: list[AnalysisQueryColumn]
    rows: list[AnalysisQueryRow]
    totals: dict[str, float | int | None] = Field(default_factory=dict)
    applied_filters: list[AnalysisFilter] = Field(default_factory=list)

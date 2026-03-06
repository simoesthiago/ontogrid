from datetime import datetime

from pydantic import BaseModel


class AssetCreate(BaseModel):
    external_ref: str | None = None
    name: str
    asset_type: str
    substation_name: str | None = None
    nominal_voltage_kv: float | None = None
    criticality: str = "medium"
    status: str = "active"


class AssetResponse(AssetCreate):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


class AssetListItem(BaseModel):
    id: str
    name: str
    asset_type: str
    status: str
    criticality: str
    latest_health_score: float | None = None


class AssetListResponse(BaseModel):
    items: list[AssetListItem]
    total: int


class MeasurementItem(BaseModel):
    timestamp: datetime
    measurement_type: str
    value: float
    quality_flag: str
    source: str


class MeasurementListResponse(BaseModel):
    asset_id: str
    items: list[MeasurementItem]


class HealthPoint(BaseModel):
    score: float
    band: str
    calculated_at: datetime


class AssetHealthResponse(BaseModel):
    asset_id: str
    current: HealthPoint | None
    history: list[HealthPoint]

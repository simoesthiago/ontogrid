from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.schemas.analysis import AnalysisViewConfig


SavedViewScopeType = Literal["dataset", "entity"]


class SavedViewResponse(BaseModel):
    id: str
    user_id: str
    scope_type: SavedViewScopeType
    scope_id: str
    name: str
    description: str | None = None
    config_json: AnalysisViewConfig
    created_at: str
    updated_at: str


class SavedViewListResponse(BaseModel):
    items: list[SavedViewResponse]
    total: int


class SavedViewCreateRequest(BaseModel):
    scope_type: SavedViewScopeType
    scope_id: str
    name: str
    description: str | None = None
    config_json: AnalysisViewConfig


class SavedViewUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    config_json: AnalysisViewConfig | None = None

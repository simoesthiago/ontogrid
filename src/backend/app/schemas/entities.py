from pydantic import BaseModel, Field

from app.schemas.graph import GraphNeighborsResponse


class EntityProfileIdentity(BaseModel):
    id: str
    entity_type: str
    canonical_code: str
    name: str
    jurisdiction: str
    attributes: dict[str, object]


class EntityProfileAliasItem(BaseModel):
    source_code: str
    alias_name: str
    external_code: str | None = None
    confidence: float | None = None


class EntityProfileSeriesItem(BaseModel):
    series_id: str
    dataset_id: str
    dataset_code: str
    metric_code: str
    metric_name: str
    unit: str
    temporal_granularity: str
    semantic_value_type: str
    reference_time_kind: str
    latest_observation_at: str
    latest_value: float | str | None


class EntityProfileVersionItem(BaseModel):
    dataset_version_id: str
    label: str
    published_at: str | None = None
    dataset_id: str
    dataset_code: str


class EntityProfileEvidenceItem(BaseModel):
    id: str
    scope_type: str
    scope_id: str
    dataset_version_id: str
    series_id: str | None = None
    selector: dict[str, object] = Field(default_factory=dict)
    claim_text: str
    created_at: str | None = None


class EntityProfileFacets(BaseModel):
    party: dict[str, object] | None = None
    agent_profile: list[dict[str, object]] = Field(default_factory=list)
    generation_asset: dict[str, object] | None = None
    geo: list[dict[str, object]] = Field(default_factory=list)
    regulatory: dict[str, object] | None = None


class EntityProfileResponse(BaseModel):
    identity: EntityProfileIdentity
    aliases: list[EntityProfileAliasItem]
    semantic_type: str
    facets: EntityProfileFacets
    series: list[EntityProfileSeriesItem]
    neighbors: GraphNeighborsResponse | None = None
    recent_versions: list[EntityProfileVersionItem]
    evidence: list[EntityProfileEvidenceItem]
    graph_status: str

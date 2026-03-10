from pydantic import BaseModel


class GraphEntityItem(BaseModel):
    id: str
    entity_type: str
    canonical_code: str
    name: str
    aliases: list[str]
    jurisdiction: str


class GraphEntityListResponse(BaseModel):
    items: list[GraphEntityItem]
    total: int


class GraphEntityDetailResponse(BaseModel):
    id: str
    entity_type: str
    canonical_code: str
    name: str
    attributes: dict[str, object]


class GraphNode(BaseModel):
    id: str
    type: str
    name: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphProvenance(BaseModel):
    dataset_version_ids: list[str]


class GraphNeighborsResponse(BaseModel):
    entity_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    provenance: GraphProvenance

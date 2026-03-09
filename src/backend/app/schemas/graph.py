from pydantic import BaseModel


class GraphEntityItem(BaseModel):
    id: str
    entity_type: str
    name: str
    source: str
    alias_count: int


class GraphEntityListResponse(BaseModel):
    items: list[GraphEntityItem]
    total: int


class GraphNode(BaseModel):
    id: str
    type: str
    name: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphNeighborsResponse(BaseModel):
    entity_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]

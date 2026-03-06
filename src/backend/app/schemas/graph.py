from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    type: str
    name: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class NeighborsResponse(BaseModel):
    asset_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ImpactedAsset(BaseModel):
    id: str
    name: str
    reason: str


class ImpactedSubstation(BaseModel):
    id: str
    name: str


class ImpactResponse(BaseModel):
    asset_id: str
    impacted_assets: list[ImpactedAsset]
    impacted_substations: list[ImpactedSubstation]

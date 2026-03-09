from fastapi import APIRouter, HTTPException, status

from app.schemas.graph import GraphEntityItem, GraphEntityListResponse, GraphNeighborsResponse
from app.services.public_data_store import store

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/entities", response_model=GraphEntityListResponse)
def list_entities(
    q: str | None = None,
    entity_type: str | None = None,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> GraphEntityListResponse:
    items = store.list_entities(q=q, entity_type=entity_type, source=source)
    window = items[offset : offset + limit]
    return GraphEntityListResponse(items=[GraphEntityItem(**item) for item in window], total=len(items))


@router.get("/entities/{entity_id}/neighbors", response_model=GraphNeighborsResponse)
def get_neighbors(entity_id: str) -> GraphNeighborsResponse:
    result = store.get_neighbors(entity_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return GraphNeighborsResponse(**result)

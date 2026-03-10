from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.graph import (
    GraphEntityDetailResponse,
    GraphEntityItem,
    GraphEntityListResponse,
    GraphNeighborsResponse,
)
from app.services.graph_service import GraphBackendUnavailable, get_graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/entities", response_model=GraphEntityListResponse)
def list_entities(
    q: str | None = None,
    entity_type: str | None = None,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> GraphEntityListResponse:
    try:
        items, total = get_graph_service().list_entities(
            db,
            q=q,
            entity_type=entity_type,
            source=source,
            limit=limit,
            offset=offset,
        )
    except GraphBackendUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return GraphEntityListResponse(items=[GraphEntityItem(**item) for item in items], total=total)


@router.get("/entities/{entity_id}", response_model=GraphEntityDetailResponse)
def get_entity(entity_id: str, db: Session = Depends(get_db)) -> GraphEntityDetailResponse:
    try:
        result = get_graph_service().get_entity(db, entity_id)
    except GraphBackendUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return GraphEntityDetailResponse(**result)


@router.get("/entities/{entity_id}/neighbors", response_model=GraphNeighborsResponse)
def get_neighbors(entity_id: str, db: Session = Depends(get_db)) -> GraphNeighborsResponse:
    try:
        result = get_graph_service().get_neighbors(db, entity_id)
    except GraphBackendUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return GraphNeighborsResponse(**result)

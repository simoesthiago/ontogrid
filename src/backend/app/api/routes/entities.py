from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.entities import EntityListItem, EntityListResponse, EntityProfileResponse
from app.services.entity_profile_service import entity_profile_service

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("", response_model=EntityListResponse)
def list_entities(
    q: str | None = None,
    entity_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> EntityListResponse:
    items, total = entity_profile_service.list_entities(
        db,
        q=q,
        entity_type=entity_type,
        limit=limit,
        offset=offset,
    )
    return EntityListResponse(items=[EntityListItem(**item) for item in items], total=total)


@router.get("/{entity_id}/profile", response_model=EntityProfileResponse)
def get_entity_profile(entity_id: str, db: Session = Depends(get_db)) -> EntityProfileResponse:
    result = entity_profile_service.get_profile(db, entity_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return EntityProfileResponse(**result)

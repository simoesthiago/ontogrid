from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.entities import EntityProfileResponse
from app.services.entity_profile_service import entity_profile_service

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("/{entity_id}/profile", response_model=EntityProfileResponse)
def get_entity_profile(entity_id: str, db: Session = Depends(get_db)) -> EntityProfileResponse:
    result = entity_profile_service.get_profile(db, entity_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return EntityProfileResponse(**result)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_demo_user_id
from app.db import get_db
from app.schemas.views import (
    SavedViewCreateRequest,
    SavedViewListResponse,
    SavedViewResponse,
    SavedViewScopeType,
    SavedViewUpdateRequest,
)
from app.services.view_service import UNSET, view_service

router = APIRouter(prefix="/views", tags=["views"])


@router.get("", response_model=SavedViewListResponse)
def list_saved_views(
    scope_type: SavedViewScopeType,
    scope_id: str,
    user_id: str = Depends(get_demo_user_id),
    db: Session = Depends(get_db),
) -> SavedViewListResponse:
    items, total = view_service.list_views(
        db,
        user_id=user_id,
        scope_type=scope_type,
        scope_id=scope_id,
    )
    return SavedViewListResponse(items=[SavedViewResponse(**item) for item in items], total=total)


@router.post("", response_model=SavedViewResponse, status_code=status.HTTP_201_CREATED)
def create_saved_view(
    payload: SavedViewCreateRequest,
    user_id: str = Depends(get_demo_user_id),
    db: Session = Depends(get_db),
) -> SavedViewResponse:
    item = view_service.create_view(
        db,
        user_id=user_id,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        name=payload.name,
        description=payload.description,
        config_json=payload.config_json.model_dump(),
    )
    return SavedViewResponse(**item)


@router.patch("/{view_id}", response_model=SavedViewResponse)
def update_saved_view(
    view_id: str,
    payload: SavedViewUpdateRequest,
    user_id: str = Depends(get_demo_user_id),
    db: Session = Depends(get_db),
) -> SavedViewResponse:
    fields_set = payload.model_fields_set
    item = view_service.update_view(
        db,
        user_id=user_id,
        view_id=view_id,
        name=payload.name if "name" in fields_set else UNSET,
        description=payload.description if "description" in fields_set else UNSET,
        config_json=payload.config_json.model_dump() if "config_json" in fields_set and payload.config_json is not None else UNSET,
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved view not found")
    return SavedViewResponse(**item)


@router.delete("/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_view(
    view_id: str,
    user_id: str = Depends(get_demo_user_id),
    db: Session = Depends(get_db),
) -> Response:
    deleted = view_service.delete_view(db, user_id=user_id, view_id=view_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved view not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

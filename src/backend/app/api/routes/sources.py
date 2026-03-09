from fastapi import APIRouter, Depends

from app.db import get_db
from app.schemas.sources import SourceItem, SourceListResponse
from app.services.catalog_service import catalog_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=SourceListResponse)
def list_sources(
    db: Session = Depends(get_db),
    q: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> SourceListResponse:
    items, total = catalog_service.list_sources(db, q=q, status=status, limit=limit, offset=offset)
    return SourceListResponse(items=[SourceItem(**item) for item in items], total=total)

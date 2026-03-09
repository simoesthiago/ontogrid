from fastapi import APIRouter

from app.schemas.sources import SourceItem, SourceListResponse
from app.services.public_data_store import store

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=SourceListResponse)
def list_sources(
    q: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> SourceListResponse:
    items = store.list_sources(q=q, status=status)
    window = items[offset : offset + limit]
    return SourceListResponse(items=[SourceItem(**item) for item in window], total=len(items))

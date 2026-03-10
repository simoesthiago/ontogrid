from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.series import ObservationListResponse, SeriesListItem, SeriesListResponse
from app.services.series_service import series_service

router = APIRouter(prefix="/series", tags=["series"])


@router.get("", response_model=SeriesListResponse)
def list_series(
    dataset_id: str | None = None,
    entity_id: str | None = None,
    metric_code: str | None = None,
    interval: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> SeriesListResponse:
    del interval
    items, total = series_service.list_series(
        db,
        dataset_id=dataset_id,
        entity_id=entity_id,
        metric_code=metric_code,
        q=q,
        limit=limit,
        offset=offset,
    )
    return SeriesListResponse(items=[SeriesListItem(**item) for item in items], total=total)


@router.get("/{series_id}/observations", response_model=ObservationListResponse)
def get_series_observations(
    series_id: str,
    start: str | None = None,
    end: str | None = None,
    bucket: str | None = None,
    entity_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> ObservationListResponse:
    del bucket
    result = series_service.get_observations(
        db,
        series_id=series_id,
        start=start,
        end=end,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    return ObservationListResponse(**result)

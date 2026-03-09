from fastapi import APIRouter, HTTPException, status

from app.schemas.series import ObservationListResponse, SeriesListItem, SeriesListResponse
from app.services.public_data_store import store

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
) -> SeriesListResponse:
    del interval
    items = store.list_series(dataset_id=dataset_id, entity_id=entity_id, metric_code=metric_code, q=q)
    window = items[offset : offset + limit]
    return SeriesListResponse(items=[SeriesListItem(**item) for item in window], total=len(items))


@router.get("/{series_id}/observations", response_model=ObservationListResponse)
def get_series_observations(
    series_id: str,
    start: str | None = None,
    end: str | None = None,
    bucket: str | None = None,
    entity_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> ObservationListResponse:
    del start, end, bucket, entity_id
    result = store.get_observations(series_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    items = result["items"][offset : offset + limit]
    return ObservationListResponse(series_id=series_id, dataset_version_id=result["dataset_version_id"], items=items)

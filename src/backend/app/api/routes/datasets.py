from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db, get_session_factory
from app.schemas.datasets import (
    DatasetDetailResponse,
    DatasetListItem,
    DatasetListResponse,
    DatasetRefreshResponse,
    DatasetVersionDetailResponse,
    DatasetVersionItem,
    DatasetVersionListResponse,
)
from app.services.catalog_service import catalog_service
from app.services.refresh_service import RefreshService

router = APIRouter(tags=["datasets"])


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets(
    db: Session = Depends(get_db),
    source: str | None = None,
    domain: str | None = None,
    granularity: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> DatasetListResponse:
    items, total = catalog_service.list_datasets(
        db,
        source=source,
        domain=domain,
        granularity=granularity,
        q=q,
        limit=limit,
        offset=offset,
    )
    return DatasetListResponse(items=[DatasetListItem(**item) for item in items], total=total)


@router.get("/datasets/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)) -> DatasetDetailResponse:
    item = catalog_service.get_dataset(db, dataset_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return DatasetDetailResponse(**item)


@router.get("/datasets/{dataset_id}/versions", response_model=DatasetVersionListResponse)
def list_dataset_versions(dataset_id: str, db: Session = Depends(get_db)) -> DatasetVersionListResponse:
    if not catalog_service.dataset_exists(db, dataset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    items = catalog_service.list_dataset_versions(db, dataset_id)
    return DatasetVersionListResponse(dataset_id=dataset_id, items=[DatasetVersionItem(**item) for item in items])


@router.get("/datasets/{dataset_id}/versions/{version_id}", response_model=DatasetVersionDetailResponse)
def get_dataset_version(dataset_id: str, version_id: str, db: Session = Depends(get_db)) -> DatasetVersionDetailResponse:
    item = catalog_service.get_dataset_version(db, dataset_id, version_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")
    return DatasetVersionDetailResponse(**item)


@router.post("/admin/datasets/{dataset_id}/refresh", response_model=DatasetRefreshResponse, status_code=status.HTTP_202_ACCEPTED)
def request_dataset_refresh(
    dataset_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> DatasetRefreshResponse:
    if not catalog_service.dataset_exists(db, dataset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    refresh_service = RefreshService(get_session_factory())
    try:
        job = refresh_service.queue_refresh(dataset_id, trigger_type="manual")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    background_tasks.add_task(refresh_service.run_refresh, job.id)
    return DatasetRefreshResponse(**refresh_service.serialize_refresh_job(job))

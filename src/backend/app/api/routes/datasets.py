from fastapi import APIRouter, HTTPException, status

from app.schemas.datasets import (
    DatasetDetailResponse,
    DatasetListItem,
    DatasetListResponse,
    DatasetRefreshResponse,
    DatasetVersionDetailResponse,
    DatasetVersionItem,
    DatasetVersionListResponse,
)
from app.services.public_data_store import store

router = APIRouter(tags=["datasets"])


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets(
    source: str | None = None,
    domain: str | None = None,
    granularity: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> DatasetListResponse:
    items = store.list_datasets(source=source, domain=domain, granularity=granularity, q=q)
    window = items[offset : offset + limit]
    response_items = []
    for item in window:
        response_items.append(
            DatasetListItem(
                id=item["id"],
                source_code=item["source_code"],
                code=item["code"],
                name=item["name"],
                domain=item["domain"],
                granularity=item["granularity"],
                latest_version=item["latest_version"]["label"],
                latest_published_at=item["latest_published_at"],
                freshness_status=item["freshness_status"],
            )
        )
    return DatasetListResponse(items=response_items, total=len(items))


@router.get("/datasets/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(dataset_id: str) -> DatasetDetailResponse:
    item = store.get_dataset(dataset_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return DatasetDetailResponse(**item)


@router.get("/datasets/{dataset_id}/versions", response_model=DatasetVersionListResponse)
def list_dataset_versions(dataset_id: str) -> DatasetVersionListResponse:
    if store.get_dataset(dataset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    items = store.list_dataset_versions(dataset_id)
    return DatasetVersionListResponse(dataset_id=dataset_id, items=[DatasetVersionItem(**item) for item in items])


@router.get("/datasets/{dataset_id}/versions/{version_id}", response_model=DatasetVersionDetailResponse)
def get_dataset_version(dataset_id: str, version_id: str) -> DatasetVersionDetailResponse:
    item = store.get_dataset_version(dataset_id, version_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")
    return DatasetVersionDetailResponse(**item)


@router.post("/admin/datasets/{dataset_id}/refresh", response_model=DatasetRefreshResponse, status_code=status.HTTP_202_ACCEPTED)
def request_dataset_refresh(dataset_id: str) -> DatasetRefreshResponse:
    if store.get_dataset(dataset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return DatasetRefreshResponse(**store.create_refresh_job(dataset_id))

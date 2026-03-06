from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_request_context
from app.schemas.assets import (
    AssetCreate,
    AssetHealthResponse,
    AssetListItem,
    AssetListResponse,
    AssetResponse,
    HealthPoint,
    MeasurementItem,
    MeasurementListResponse,
)
from app.schemas.auth import RequestContext
from app.services.demo_store import store

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse)
def list_assets(
    q: str | None = None,
    asset_type: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    context: RequestContext = Depends(get_request_context),
) -> AssetListResponse:
    items = store.list_assets(context.tenant_id, q, asset_type, status_filter)
    result = []
    for item in items:
        current, _ = store.get_health(item["id"])
        result.append(
            AssetListItem(
                id=item["id"],
                name=item["name"],
                asset_type=item["asset_type"],
                status=item["status"],
                criticality=item["criticality"],
                latest_health_score=current["score"] if current else None,
            )
        )
    return AssetListResponse(items=result, total=len(result))


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, context: RequestContext = Depends(get_request_context)) -> AssetResponse:
    return AssetResponse(**store.create_asset(context.tenant_id, payload))


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: str, context: RequestContext = Depends(get_request_context)) -> AssetResponse:
    item = store.get_asset(context.tenant_id, asset_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return AssetResponse(**item)


@router.get("/{asset_id}/measurements", response_model=MeasurementListResponse)
def get_asset_measurements(
    asset_id: str,
    measurement_type: str | None = None,
    limit: int = 100,
    context: RequestContext = Depends(get_request_context),
) -> MeasurementListResponse:
    if store.get_asset(context.tenant_id, asset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    items = [MeasurementItem(**item) for item in store.list_measurements(context.tenant_id, asset_id, measurement_type, limit)]
    return MeasurementListResponse(asset_id=asset_id, items=items)


@router.get("/{asset_id}/health", response_model=AssetHealthResponse)
def get_asset_health(asset_id: str, context: RequestContext = Depends(get_request_context)) -> AssetHealthResponse:
    if store.get_asset(context.tenant_id, asset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    current, history = store.get_health(asset_id)
    return AssetHealthResponse(
        asset_id=asset_id,
        current=HealthPoint(**current) if current else None,
        history=[HealthPoint(**item) for item in history],
    )

from fastapi import APIRouter, Depends

from app.core.auth import get_request_context
from app.schemas.auth import RequestContext
from app.schemas.graph import ImpactResponse, NeighborsResponse
from app.services.demo_store import store

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/assets/{asset_id}/neighbors", response_model=NeighborsResponse)
def get_neighbors(asset_id: str, context: RequestContext = Depends(get_request_context)) -> NeighborsResponse:
    return NeighborsResponse(**store.get_neighbors(context.tenant_id, asset_id))


@router.get("/assets/{asset_id}/impact", response_model=ImpactResponse)
def get_impact(asset_id: str, context: RequestContext = Depends(get_request_context)) -> ImpactResponse:
    return ImpactResponse(**store.get_impact(context.tenant_id, asset_id))

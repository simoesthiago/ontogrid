from fastapi import APIRouter, Depends, status

from app.core.auth import get_request_context
from app.schemas.auth import RequestContext
from app.schemas.cases import CaseCreate, CaseListResponse, CaseResponse
from app.services.demo_store import store

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=CaseListResponse)
def list_cases(context: RequestContext = Depends(get_request_context)) -> CaseListResponse:
    items = store.list_cases(context.tenant_id)
    return CaseListResponse(items=[CaseResponse(**item) for item in items], total=len(items))


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, context: RequestContext = Depends(get_request_context)) -> CaseResponse:
    return CaseResponse(**store.create_case(context.tenant_id, payload))

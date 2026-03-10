from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.copilot.service import CopilotProviderUnavailable, copilot_service
from app.db import get_db
from app.schemas.copilot import CopilotQueryRequest, CopilotQueryResponse

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/query", response_model=CopilotQueryResponse)
def query_copilot(
    payload: CopilotQueryRequest,
    db: Session = Depends(get_db),
) -> CopilotQueryResponse:
    try:
        response = copilot_service.query(db, payload)
    except CopilotProviderUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return CopilotQueryResponse(**response)

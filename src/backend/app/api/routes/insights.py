from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.insights import EntityInsightResponse, InsightOverviewResponse
from app.services.insight_service import insight_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/overview", response_model=InsightOverviewResponse)
def get_overview(
    domain: str | None = None,
    period: str | None = None,
    db: Session = Depends(get_db),
) -> InsightOverviewResponse:
    return InsightOverviewResponse(**insight_service.get_overview(db, domain=domain, period=period))


@router.get("/entities/{entity_id}", response_model=EntityInsightResponse)
def get_entity_insights(entity_id: str, db: Session = Depends(get_db)) -> EntityInsightResponse:
    result = insight_service.get_entity_insights(db, entity_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return EntityInsightResponse(**result)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.analysis import AnalysisFieldsResponse, AnalysisQueryRequest, AnalysisQueryResponse
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/datasets/{dataset_id}/fields", response_model=AnalysisFieldsResponse)
def get_dataset_fields(dataset_id: str, db: Session = Depends(get_db)) -> AnalysisFieldsResponse:
    result = analysis_service.get_fields(db, dataset_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return AnalysisFieldsResponse(**result)


@router.post("/query", response_model=AnalysisQueryResponse)
def run_analysis_query(payload: AnalysisQueryRequest, db: Session = Depends(get_db)) -> AnalysisQueryResponse:
    try:
        result = analysis_service.run_query(db, payload.config.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AnalysisQueryResponse(**result)

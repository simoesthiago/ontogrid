from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.coverage import CatalogCoverageFamilyItem, CatalogCoverageResponse, CatalogCoverageSourceItem
from app.services.coverage_service import coverage_service

router = APIRouter(tags=["coverage"])


@router.get("/catalog/coverage", response_model=CatalogCoverageResponse)
def get_catalog_coverage(db: Session = Depends(get_db)) -> CatalogCoverageResponse:
    payload = coverage_service.get_catalog_coverage(db)
    return CatalogCoverageResponse(
        inventoried_total=payload["inventoried_total"],
        documented_only_total=payload["documented_only_total"],
        adapter_enabled_total=payload["adapter_enabled_total"],
        published_total=payload["published_total"],
        sources=[CatalogCoverageSourceItem(**item) for item in payload["sources"]],
        families=[CatalogCoverageFamilyItem(**item) for item in payload["families"]],
    )

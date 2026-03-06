from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from app.core.auth import get_request_context
from app.schemas.auth import RequestContext
from app.schemas.ingestion import IngestionJobResponse, JsonBatchJobRequest
from app.services.demo_store import store

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/jobs", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_ingestion_job(
    request: Request,
    context: RequestContext = Depends(get_request_context),
) -> IngestionJobResponse:
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("application/json"):
        payload = JsonBatchJobRequest(**await request.json())
        accepted, rejected = store.ingest_records(context.tenant_id, payload.records)
        job = store.create_job(
            tenant_id=context.tenant_id,
            source_type=payload.source_type,
            payload_format=payload.payload_format,
            received=len(payload.records),
            accepted=accepted,
            rejected=rejected,
        )
        return IngestionJobResponse(**job)

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        source_type = str(form.get("source_type", "file_upload"))
        payload_format = str(form.get("payload_format", "csv"))
        file = form.get("file")
        if not isinstance(file, UploadFile) and not hasattr(file, "read"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file is required")

        text = (await file.read()).decode("utf-8", errors="ignore")
        rows = [row for row in text.splitlines() if row.strip()]
        job = store.create_job(
            tenant_id=context.tenant_id,
            source_type=source_type,
            payload_format=payload_format,
            received=max(len(rows) - 1, 0),
            accepted=max(len(rows) - 1, 0),
            rejected=0,
        )
        return IngestionJobResponse(**job)

    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported content type")


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
def get_ingestion_job(job_id: str, context: RequestContext = Depends(get_request_context)) -> IngestionJobResponse:
    job = store.get_job(context.tenant_id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return IngestionJobResponse(**job)

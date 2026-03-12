from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Dataset, RefreshJob
from app.services.catalog_service import to_iso8601


class RefreshJobService:
    def list_jobs(
        self,
        session: Session,
        *,
        dataset_id: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        query: Select[tuple[RefreshJob]] = (
            select(RefreshJob)
            .options(
                joinedload(RefreshJob.dataset).joinedload(Dataset.source),
                joinedload(RefreshJob.published_version),
            )
            .order_by(RefreshJob.created_at.desc())
        )
        if dataset_id:
            query = query.where(RefreshJob.dataset_id == dataset_id)
        if status:
            query = query.where(RefreshJob.status == status)
        total = session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
        rows = session.scalars(query.offset(offset).limit(limit)).unique().all()
        return [self._serialize_job(row) for row in rows], total

    def get_job(self, session: Session, refresh_job_id: str) -> dict[str, object] | None:
        job = session.scalar(
            select(RefreshJob)
            .options(
                joinedload(RefreshJob.dataset).joinedload(Dataset.source),
                joinedload(RefreshJob.published_version),
            )
            .where(RefreshJob.id == refresh_job_id)
        )
        if job is None:
            return None
        return self._serialize_job(job)

    def _serialize_job(self, job: RefreshJob) -> dict[str, object]:
        dataset = job.dataset
        published_version = job.published_version
        return {
            "id": job.id,
            "dataset_id": job.dataset_id,
            "dataset_code": dataset.code if dataset else "",
            "dataset_name": dataset.name if dataset else "",
            "source_code": dataset.source.code if dataset and dataset.source else "",
            "trigger_type": job.trigger_type,
            "status": job.status,
            "rows_read": job.rows_read,
            "rows_written": job.rows_written,
            "error_summary": job.error_summary,
            "created_at": to_iso8601(job.created_at) or "",
            "started_at": to_iso8601(job.started_at),
            "finished_at": to_iso8601(job.finished_at),
            "published_version_id": published_version.id if published_version else None,
            "published_version_label": published_version.label if published_version else None,
        }


refresh_job_service = RefreshJobService()

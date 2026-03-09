from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db.models import Dataset, DatasetVersion, RefreshJob
from app.ingestion import get_adapter
from app.services.catalog_service import to_iso8601

logger = logging.getLogger(__name__)


class RefreshService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory
        self._lock = Lock()

    def queue_refresh(self, dataset_id: str, trigger_type: str) -> RefreshJob:
        with self.session_factory() as session:
            dataset = session.get(Dataset, dataset_id)
            if dataset is None:
                raise ValueError(f"Dataset {dataset_id} not found")

            active_job = session.scalar(
                select(RefreshJob)
                .where(
                    RefreshJob.dataset_id == dataset_id,
                    RefreshJob.status.in_(("queued", "running")),
                )
                .order_by(RefreshJob.created_at.desc())
            )
            if active_job is not None:
                return active_job

            job = RefreshJob(
                id=str(uuid4()),
                dataset_id=dataset.id,
                source_type=dataset.source.refresh_strategy if dataset.source else "scheduled_download",
                trigger_type=trigger_type,
                status="queued",
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job

    def run_refresh(self, refresh_job_id: str, bootstrap: bool = False) -> None:
        settings = get_settings()
        with self._lock:
            with self.session_factory() as session:
                job = session.get(RefreshJob, refresh_job_id)
                if job is None:
                    return

                dataset = session.get(Dataset, job.dataset_id)
                if dataset is None:
                    return

                adapter = get_adapter(dataset.code)
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
                session.commit()

                try:
                    raw_bytes = adapter.bootstrap_bytes() if bootstrap else adapter.fetch_bytes(settings)
                    checksum = adapter.checksum(raw_bytes)
                    parsed = adapter.parse(raw_bytes, checksum)
                    artifact_path = self._write_artifact(dataset.code, parsed.label, checksum, raw_bytes, adapter.file_extension, settings)
                    job.rows_read = parsed.row_count

                    latest_version = session.scalar(
                        select(DatasetVersion)
                        .where(DatasetVersion.dataset_id == dataset.id)
                        .order_by(DatasetVersion.published_at.desc())
                    )
                    if latest_version is not None and latest_version.checksum == checksum:
                        job.status = "published"
                        job.rows_written = 0
                        job.error_summary = "Artifact checksum matches latest published version"
                        job.finished_at = datetime.now(timezone.utc)
                        session.commit()
                        logger.info(
                            "refresh-deduplicated source_code=%s dataset_code=%s refresh_job_id=%s version_id=%s",
                            dataset.source.code,
                            dataset.code,
                            job.id,
                            latest_version.id,
                        )
                        return

                    version = DatasetVersion(
                        id=str(uuid4()),
                        dataset_id=dataset.id,
                        label=parsed.label,
                        extracted_at=parsed.extracted_at,
                        published_at=parsed.published_at,
                        coverage_start=parsed.coverage_start,
                        coverage_end=parsed.coverage_end,
                        row_count=parsed.row_count,
                        schema_version=parsed.schema_version,
                        checksum=checksum,
                        status="published",
                        lineage={
                            "source_code": dataset.source.code,
                            "refresh_job_id": job.id,
                            "artifact_checksum": checksum,
                            **adapter.artifact_metadata(artifact_path, raw_bytes),
                        },
                    )
                    session.add(version)
                    session.flush()

                    dataset.latest_version_id = version.id
                    job.status = "published"
                    job.rows_written = parsed.row_count
                    job.finished_at = datetime.now(timezone.utc)
                    job.published_version_id = version.id
                    session.commit()
                    logger.info(
                        "refresh-published source_code=%s dataset_code=%s refresh_job_id=%s version_id=%s",
                        dataset.source.code,
                        dataset.code,
                        job.id,
                        version.id,
                    )
                except Exception as exc:
                    session.rollback()
                    failed_job = session.get(RefreshJob, refresh_job_id)
                    if failed_job is not None:
                        failed_job.status = "failed"
                        failed_job.error_summary = str(exc)
                        failed_job.finished_at = datetime.now(timezone.utc)
                        session.commit()
                    logger.exception(
                        "refresh-failed dataset_code=%s refresh_job_id=%s error=%s",
                        dataset.code,
                        refresh_job_id,
                        exc,
                    )

    def bootstrap_missing_versions(self) -> None:
        with self.session_factory() as session:
            dataset_ids = session.scalars(
                select(Dataset.id).where(~Dataset.versions.any()).order_by(Dataset.code)
            ).all()

        for dataset_id in dataset_ids:
            job = self.queue_refresh(dataset_id, trigger_type="manual")
            self.run_refresh(job.id, bootstrap=True)

    def run_due_refreshes(self, force: bool = False) -> int:
        dataset_ids: list[str] = []
        with self.session_factory() as session:
            datasets = session.scalars(select(Dataset).order_by(Dataset.code)).all()
            for dataset in datasets:
                if force or self._is_due(dataset, session):
                    dataset_ids.append(dataset.id)

        runs = 0
        for dataset_id in dataset_ids:
            job = self.queue_refresh(dataset_id, trigger_type="schedule")
            self.run_refresh(job.id)
            runs += 1
        return runs

    def serialize_refresh_job(self, refresh_job: RefreshJob) -> dict[str, str]:
        return {
            "refresh_job_id": refresh_job.id,
            "dataset_id": refresh_job.dataset_id,
            "status": refresh_job.status,
            "requested_at": to_iso8601(refresh_job.created_at) or "",
        }

    def _is_due(self, dataset: Dataset, session: Session) -> bool:
        active_job = session.scalar(
            select(RefreshJob)
            .where(RefreshJob.dataset_id == dataset.id, RefreshJob.status.in_(("queued", "running")))
            .limit(1)
        )
        if active_job is not None:
            return False

        latest_version = session.scalar(
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset.id)
            .order_by(DatasetVersion.published_at.desc())
        )
        if latest_version is None:
            return True

        now = datetime.now(timezone.utc)
        age = now - latest_version.published_at.astimezone(timezone.utc)
        if dataset.refresh_frequency == "daily":
            return age.total_seconds() >= 86400
        if dataset.refresh_frequency == "monthly":
            return age.total_seconds() >= 86400 * 30
        return False

    def _write_artifact(
        self,
        dataset_code: str,
        label: str,
        checksum: str,
        raw_bytes: bytes,
        file_extension: str,
        settings: Settings,
    ) -> Path:
        safe_label = label.replace(":", "-")
        target_dir = settings.artifacts_path / dataset_code
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{safe_label}__{checksum[:12]}{file_extension}"
        target_path.write_bytes(raw_bytes)
        return target_path

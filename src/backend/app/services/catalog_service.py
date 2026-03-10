from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Dataset, DatasetVersion, Source
from app.ingestion.registry import has_adapter


def to_iso8601(value: datetime | None) -> str | None:
    if value is None:
        return None
    as_utc = value.astimezone(timezone.utc)
    return as_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")


class CatalogService:
    def list_sources(self, session: Session, q: str | None, status: str | None, limit: int, offset: int) -> tuple[list[dict], int]:
        query: Select[tuple[Source]] = select(Source).order_by(Source.name)
        if q:
            term = f"%{q.lower()}%"
            query = query.where(or_(func.lower(Source.name).like(term), func.lower(Source.code).like(term)))
        if status:
            query = query.where(Source.status == status)
        total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = session.scalars(query.offset(offset).limit(limit)).all()
        items = [
            {
                "id": row.id,
                "code": row.code,
                "name": row.name,
                "authority_type": row.authority_type,
                "refresh_strategy": row.refresh_strategy,
                "status": row.status,
            }
            for row in rows
        ]
        return items, total

    def list_datasets(
        self,
        session: Session,
        source: str | None,
        domain: str | None,
        granularity: str | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict], int]:
        query: Select[tuple[Dataset]] = (
            select(Dataset)
            .options(joinedload(Dataset.source), joinedload(Dataset.latest_version))
            .order_by(Dataset.name)
        )
        if source:
            query = query.join(Dataset.source).where(Source.code == source)
        if domain:
            query = query.where(Dataset.domain == domain)
        if granularity:
            query = query.where(Dataset.granularity == granularity)
        if q:
            term = f"%{q.lower()}%"
            query = query.where(or_(func.lower(Dataset.name).like(term), func.lower(Dataset.code).like(term)))
        total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = session.scalars(query.offset(offset).limit(limit)).unique().all()
        return [self._serialize_dataset_list_item(row) for row in rows], total

    def get_dataset(self, session: Session, dataset_id: str) -> dict | None:
        dataset = session.scalar(
            select(Dataset)
            .options(joinedload(Dataset.source), joinedload(Dataset.latest_version))
            .where(Dataset.id == dataset_id)
        )
        if dataset is None:
            return None
        latest = dataset.latest_version
        return {
            "id": dataset.id,
            "source_id": dataset.source_id,
            "source_code": dataset.source.code,
            "code": dataset.code,
            "name": dataset.name,
            "domain": dataset.domain,
            "description": dataset.description,
            "granularity": dataset.granularity,
            "refresh_frequency": dataset.refresh_frequency,
            "schema_summary": dataset.schema_summary,
            "latest_version": {
                "id": latest.id if latest else "",
                "label": latest.label if latest else "",
                "published_at": to_iso8601(latest.published_at) if latest else "",
            },
            "adapter_enabled": has_adapter(dataset.code),
            "ingestion_status": self._ingestion_status(dataset),
        }

    def list_dataset_versions(self, session: Session, dataset_id: str) -> list[dict]:
        versions = session.scalars(
            select(DatasetVersion).where(DatasetVersion.dataset_id == dataset_id).order_by(DatasetVersion.published_at.desc())
        ).all()
        return [self._serialize_dataset_version_item(version) for version in versions]

    def get_dataset_version(self, session: Session, dataset_id: str, version_id: str) -> dict | None:
        version = session.scalar(
            select(DatasetVersion).where(DatasetVersion.dataset_id == dataset_id, DatasetVersion.id == version_id)
        )
        if version is None:
            return None
        payload = self._serialize_dataset_version_item(version)
        payload.update(
            {
                "dataset_id": version.dataset_id,
                "row_count": version.row_count,
                "schema_version": version.schema_version,
                "lineage": version.lineage,
            }
        )
        return payload

    def dataset_exists(self, session: Session, dataset_id: str) -> bool:
        return session.scalar(select(func.count()).select_from(Dataset).where(Dataset.id == dataset_id)) == 1

    def _serialize_dataset_list_item(self, dataset: Dataset) -> dict:
        latest_version = dataset.latest_version
        return {
            "id": dataset.id,
            "source_code": dataset.source.code,
            "code": dataset.code,
            "name": dataset.name,
            "domain": dataset.domain,
            "granularity": dataset.granularity,
            "latest_version": latest_version.label if latest_version else "",
            "latest_published_at": to_iso8601(latest_version.published_at) if latest_version else "",
            "freshness_status": self._freshness_status(dataset, latest_version),
            "adapter_enabled": has_adapter(dataset.code),
            "ingestion_status": self._ingestion_status(dataset),
        }

    def _serialize_dataset_version_item(self, version: DatasetVersion) -> dict:
        return {
            "id": version.id,
            "label": version.label,
            "extracted_at": to_iso8601(version.extracted_at),
            "published_at": to_iso8601(version.published_at),
            "coverage_start": to_iso8601(version.coverage_start),
            "coverage_end": to_iso8601(version.coverage_end),
            "status": version.status,
            "checksum": version.checksum,
        }

    def _freshness_status(self, dataset: Dataset, version: DatasetVersion | None) -> str:
        if version is None:
            return "stale"
        age = datetime.now(timezone.utc) - version.published_at.astimezone(timezone.utc)
        if dataset.refresh_frequency == "daily" and age.days >= 2:
            return "stale"
        if dataset.refresh_frequency == "monthly" and age.days >= 40:
            return "stale"
        return "fresh"

    def _ingestion_status(self, dataset: Dataset) -> str:
        if dataset.latest_version is not None:
            return "published"
        if has_adapter(dataset.code):
            return "adapter_enabled"
        return "documented_only"


catalog_service = CatalogService()

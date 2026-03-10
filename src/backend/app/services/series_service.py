from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Dataset, MetricSeries, Observation
from app.services.catalog_service import to_iso8601


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SeriesService:
    def list_series(
        self,
        session: Session,
        *,
        dataset_id: str | None,
        entity_id: str | None,
        metric_code: str | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        query = select(MetricSeries).order_by(MetricSeries.metric_name)
        if dataset_id:
            query = query.where(MetricSeries.dataset_id == dataset_id)
        if metric_code:
            query = query.where(MetricSeries.metric_code == metric_code)
        if entity_id:
            query = query.join(MetricSeries.observations).where(Observation.entity_id == entity_id)
        if q:
            term = f"%{q.lower()}%"
            query = query.where(
                or_(
                    func.lower(MetricSeries.metric_name).like(term),
                    func.lower(MetricSeries.metric_code).like(term),
                )
            )
        query = query.distinct()
        total = session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
        rows = session.scalars(query.offset(offset).limit(limit)).unique().all()
        return (
            [
                {
                    "id": row.id,
                    "dataset_id": row.dataset_id,
                    "metric_code": row.metric_code,
                    "metric_name": row.metric_name,
                    "unit": row.unit,
                    "temporal_granularity": row.temporal_granularity,
                    "entity_type": row.entity_type,
                    "latest_observation_at": to_iso8601(row.latest_observation_at) or "",
                }
                for row in rows
            ],
            total,
        )

    def get_observations(
        self,
        session: Session,
        *,
        series_id: str,
        start: str | None,
        end: str | None,
        entity_id: str | None,
        limit: int,
        offset: int,
    ) -> dict[str, object] | None:
        series = session.get(MetricSeries, series_id)
        if series is None:
            return None

        latest_version_id = session.scalar(
            select(Dataset.latest_version_id).where(Dataset.id == series.dataset_id)
        )
        query = (
            select(Observation)
            .where(Observation.series_id == series_id)
            .order_by(Observation.time)
        )
        if latest_version_id:
            query = query.where(Observation.dataset_version_id == latest_version_id)
        if entity_id:
            query = query.where(Observation.entity_id == entity_id)
        if (start_dt := _parse_timestamp(start)) is not None:
            query = query.where(Observation.time >= start_dt)
        if (end_dt := _parse_timestamp(end)) is not None:
            query = query.where(Observation.time <= end_dt)

        rows = session.scalars(query.offset(offset).limit(limit)).all()
        return {
            "series_id": series_id,
            "dataset_version_id": latest_version_id or "",
            "items": [
                {
                    "timestamp": to_iso8601(row.time) or "",
                    "value": row.value_numeric if row.value_numeric is not None else row.value_text,
                    "unit": series.unit,
                    "quality_flag": row.quality_flag,
                    "published_at": to_iso8601(row.published_at) or "",
                }
                for row in rows
            ],
        }


series_service = SeriesService()

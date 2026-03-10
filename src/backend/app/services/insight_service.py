from __future__ import annotations

from datetime import timezone
from uuid import uuid4

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Dataset, DatasetVersion, Entity, InsightSnapshot, MetricSeries, Observation, Relation
from app.services.catalog_service import to_iso8601


class InsightService:
    def rebuild_overview_snapshot(self, session: Session) -> dict[str, object]:
        payload = self._build_overview_payload(session)
        session.execute(
            delete(InsightSnapshot).where(
                InsightSnapshot.scope_type == "overview",
                InsightSnapshot.scope_id.is_(None),
            )
        )
        snapshot = InsightSnapshot(
            id=str(uuid4()),
            scope_type="overview",
            scope_id=None,
            title="Visao geral do hub publico",
            summary="Resumo derivado das ultimas publicacoes curadas do Energy Data Hub.",
            payload=payload,
            dataset_version_id=self._latest_dataset_version_id(session),
        )
        session.add(snapshot)
        session.flush()
        return payload

    def get_overview(self, session: Session, *, domain: str | None, period: str | None) -> dict[str, object]:
        del domain, period
        snapshot = session.scalar(
            select(InsightSnapshot)
            .where(InsightSnapshot.scope_type == "overview", InsightSnapshot.scope_id.is_(None))
            .order_by(InsightSnapshot.generated_at.desc())
        )
        if snapshot is None:
            payload = self.rebuild_overview_snapshot(session)
            session.commit()
            return payload
        return snapshot.payload

    def get_entity_insights(self, session: Session, entity_id: str) -> dict[str, object] | None:
        entity = session.get(Entity, entity_id)
        if entity is None:
            return None

        related_series = session.execute(
            select(MetricSeries.id, MetricSeries.metric_code)
            .join(Observation, Observation.series_id == MetricSeries.id)
            .where(Observation.entity_id == entity_id)
            .distinct()
        ).all()

        recent_versions = session.execute(
            select(DatasetVersion.id, DatasetVersion.published_at)
            .join(Observation, Observation.dataset_version_id == DatasetVersion.id)
            .where(Observation.entity_id == entity_id)
            .distinct()
            .order_by(DatasetVersion.published_at.desc())
            .limit(5)
        ).all()

        if not recent_versions:
            recent_versions = session.execute(
                select(DatasetVersion.id, DatasetVersion.published_at)
                .join(Relation, Relation.dataset_version_id == DatasetVersion.id)
                .where(
                    or_(
                        Relation.source_entity_id == entity_id,
                        Relation.target_entity_id == entity_id,
                    )
                )
                .distinct()
                .order_by(DatasetVersion.published_at.desc())
                .limit(5)
            ).all()

        dataset_count = session.scalar(
            select(func.count(func.distinct(Dataset.id)))
            .join(DatasetVersion, Dataset.latest_version_id == DatasetVersion.id)
            .join(Observation, Observation.dataset_version_id == DatasetVersion.id)
            .where(Observation.entity_id == entity_id)
        ) or 0

        return {
            "entity_id": entity_id,
            "summary": (
                f"A entidade aparece em {dataset_count} datasets curados e {len(related_series)} series principais."
            ),
            "related_series": [
                {"series_id": series_id, "metric_code": metric_code}
                for series_id, metric_code in related_series
            ],
            "recent_changes": [
                {
                    "dataset_version_id": version_id,
                    "message": f"Nova versao publicada em {to_iso8601(published_at) or ''}.",
                }
                for version_id, published_at in recent_versions
            ],
        }

    def _build_overview_payload(self, session: Session) -> dict[str, object]:
        cards = []
        highlights = []

        load = self._latest_series_snapshot(session, "load_mw")
        if load is not None:
            cards.append(
                {
                    "id": "load_mw_latest",
                    "title": f"Carga atual em {load['entity_name']}",
                    "value": round(load["value"], 1),
                    "unit": load["unit"],
                    "trend": load["trend"],
                }
            )

        pld = self._latest_series_snapshot(session, "pld_rs_mwh")
        if pld is not None:
            cards.append(
                {
                    "id": "pld_rs_mwh_latest",
                    "title": f"PLD atual em {pld['entity_name']}",
                    "value": round(pld["value"], 1),
                    "unit": pld["unit"],
                    "trend": pld["trend"],
                }
            )

        tariff = self._latest_average_snapshot(session, "tariff_rs_mwh")
        if tariff is not None:
            cards.append(
                {
                    "id": "tariff_rs_mwh_average",
                    "title": "Tarifa media monitorada",
                    "value": round(tariff["value"], 1),
                    "unit": tariff["unit"],
                    "trend": tariff["trend"],
                }
            )

        if load is not None and pld is not None and load["entity_id"] == pld["entity_id"]:
            highlights.append(
                {
                    "title": (
                        f"{load['entity_name']} combina carga de {round(load['value'], 1)} {load['unit']} "
                        f"e PLD de {round(pld['value'], 1)} {pld['unit']} na ultima publicacao."
                    ),
                    "dataset_version_id": pld["dataset_version_id"],
                }
            )
        if tariff is not None:
            highlights.append(
                {
                    "title": (
                        f"As tarifas monitoradas fecharam a ultima publicacao com media de "
                        f"{round(tariff['value'], 1)} {tariff['unit']}."
                    ),
                    "dataset_version_id": tariff["dataset_version_id"],
                }
            )

        return {"cards": cards, "highlights": highlights}

    def _latest_series_snapshot(self, session: Session, metric_code: str) -> dict[str, object] | None:
        row = session.execute(
            select(
                Observation.value_numeric.label("value_numeric"),
                Observation.published_at.label("published_at"),
                Observation.dataset_version_id.label("dataset_version_id"),
                MetricSeries.id.label("series_id"),
                MetricSeries.unit.label("unit"),
                Entity.id.label("entity_id"),
                Entity.name.label("entity_name"),
            )
            .join(MetricSeries, MetricSeries.id == Observation.series_id)
            .join(Entity, Entity.id == Observation.entity_id)
            .join(Dataset, Dataset.id == MetricSeries.dataset_id)
            .where(
                MetricSeries.metric_code == metric_code,
                Observation.dataset_version_id == Dataset.latest_version_id,
            )
            .order_by(Observation.time.desc())
            .limit(1)
        ).first()
        if row is None or row.value_numeric is None:
            return None

        previous = session.execute(
            select(Observation.value_numeric)
            .where(
                Observation.series_id == row.series_id,
                Observation.entity_id == row.entity_id,
            )
            .order_by(Observation.time.desc())
            .offset(1)
            .limit(1)
        ).scalar_one_or_none()
        trend = self._trend(row.value_numeric, previous)
        return {
            "value": row.value_numeric,
            "unit": row.unit,
            "entity_id": row.entity_id,
            "entity_name": row.entity_name,
            "dataset_version_id": row.dataset_version_id,
            "trend": trend,
        }

    def _latest_average_snapshot(self, session: Session, metric_code: str) -> dict[str, object] | None:
        latest_version_id = session.scalar(
            select(Dataset.latest_version_id)
            .join(MetricSeries, MetricSeries.dataset_id == Dataset.id)
            .where(MetricSeries.metric_code == metric_code)
            .limit(1)
        )
        if latest_version_id is None:
            return None

        current = session.execute(
            select(func.avg(Observation.value_numeric), MetricSeries.unit)
            .join(MetricSeries, MetricSeries.id == Observation.series_id)
            .where(
                MetricSeries.metric_code == metric_code,
                Observation.dataset_version_id == latest_version_id,
            )
            .group_by(MetricSeries.unit)
        ).first()
        if current is None or current[0] is None:
            return None

        previous_version_id = session.scalar(
            select(DatasetVersion.id)
            .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
            .join(MetricSeries, MetricSeries.dataset_id == Dataset.id)
            .where(
                MetricSeries.metric_code == metric_code,
                DatasetVersion.id != latest_version_id,
            )
            .order_by(DatasetVersion.published_at.desc())
            .limit(1)
        )
        previous_value = None
        if previous_version_id:
            previous_value = session.scalar(
                select(func.avg(Observation.value_numeric))
                .join(MetricSeries, MetricSeries.id == Observation.series_id)
                .where(
                    MetricSeries.metric_code == metric_code,
                    Observation.dataset_version_id == previous_version_id,
                )
            )
        return {
            "value": float(current[0]),
            "unit": current[1],
            "dataset_version_id": latest_version_id,
            "trend": self._trend(float(current[0]), previous_value),
        }

    def _latest_dataset_version_id(self, session: Session) -> str | None:
        return session.scalar(
            select(DatasetVersion.id).order_by(DatasetVersion.published_at.desc()).limit(1)
        )

    def _trend(self, current: float, previous: float | None) -> str:
        if previous is None:
            return "flat"
        if current > previous:
            return "up"
        if current < previous:
            return "down"
        return "flat"


insight_service = InsightService()

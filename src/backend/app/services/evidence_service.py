from __future__ import annotations

from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, aliased

from app.db.models import Entity, EvidenceRegistry, HarmonizationEvent, MetricSeries, Observation, Relation
from app.services.catalog_service import to_iso8601


class EvidenceService:
    def rebuild_dataset_version_evidence(self, session: Session, dataset_version_id: str) -> None:
        session.execute(delete(EvidenceRegistry).where(EvidenceRegistry.dataset_version_id == dataset_version_id))
        self._rebuild_harmonization_evidence(session, dataset_version_id)
        self._rebuild_relation_evidence(session, dataset_version_id)
        self._rebuild_observation_evidence(session, dataset_version_id)

    def _rebuild_harmonization_evidence(self, session: Session, dataset_version_id: str) -> None:
        rows = session.execute(
            select(
                HarmonizationEvent.id,
                HarmonizationEvent.entity_id,
                HarmonizationEvent.source_code,
                HarmonizationEvent.source_record_key,
                HarmonizationEvent.decision,
                HarmonizationEvent.match_rule,
                HarmonizationEvent.matched_on,
                HarmonizationEvent.source_identity,
                Entity.name.label("entity_name"),
            )
            .join(Entity, Entity.id == HarmonizationEvent.entity_id)
            .where(HarmonizationEvent.dataset_version_id == dataset_version_id)
            .order_by(HarmonizationEvent.created_at.desc())
        ).all()

        for row in rows:
            scope_id = f"harmonization:{row.id}"
            action = "criada" if row.decision == "created_new" else "reconciliada"
            claim_text = (
                f"{row.entity_name} foi {action} pela regra {row.match_rule} "
                f"durante a harmonizacao publica da fonte {row.source_code}."
            )
            session.add(
                EvidenceRegistry(
                    id=str(uuid4()),
                    scope_type="harmonization",
                    scope_id=scope_id,
                    dataset_version_id=dataset_version_id,
                    entity_id=row.entity_id,
                    series_id=None,
                    observation_selector={
                        "source_record_key": row.source_record_key,
                        "decision": row.decision,
                        "match_rule": row.match_rule,
                        "matched_on": row.matched_on,
                        "source_identity": row.source_identity,
                    },
                    claim_text=claim_text,
                )
            )

    def _rebuild_relation_evidence(self, session: Session, dataset_version_id: str) -> None:
        source_entity = aliased(Entity)
        target_entity = aliased(Entity)
        rows = session.execute(
            select(
                Relation.id,
                Relation.relation_type,
                Relation.source_entity_id,
                Relation.target_entity_id,
                Relation.attributes,
                source_entity.name.label("source_name"),
                target_entity.name.label("target_name"),
            )
            .join(source_entity, source_entity.id == Relation.source_entity_id)
            .join(target_entity, target_entity.id == Relation.target_entity_id)
            .where(Relation.dataset_version_id == dataset_version_id)
        ).all()

        for row in rows:
            claim_text = f"{row.source_name} possui relacao {row.relation_type} com {row.target_name}."
            session.add(
                EvidenceRegistry(
                    id=str(uuid4()),
                    scope_type="relation",
                    scope_id=f"relation:{row.id}",
                    dataset_version_id=dataset_version_id,
                    entity_id=row.source_entity_id,
                    series_id=None,
                    observation_selector={
                        "relation_type": row.relation_type,
                        "target_entity_id": row.target_entity_id,
                        "attributes": row.attributes,
                    },
                    claim_text=claim_text,
                )
            )

    def _rebuild_observation_evidence(self, session: Session, dataset_version_id: str) -> None:
        rows = session.execute(
            select(
                Observation.time,
                Observation.entity_id,
                Observation.series_id,
                Observation.dataset_version_id,
                Observation.value_numeric,
                Observation.value_text,
                Observation.quality_flag,
                MetricSeries.metric_name,
                MetricSeries.unit,
                Entity.name.label("entity_name"),
            )
            .join(MetricSeries, MetricSeries.id == Observation.series_id)
            .join(Entity, Entity.id == Observation.entity_id)
            .where(Observation.dataset_version_id == dataset_version_id)
            .order_by(Observation.time.desc())
        ).all()

        for row in rows:
            timestamp = to_iso8601(row.time) or ""
            value = row.value_numeric if row.value_numeric is not None else row.value_text
            evidence = EvidenceRegistry(
                id=str(uuid4()),
                scope_type="observation",
                scope_id=self.observation_scope_id(row.series_id, row.entity_id, timestamp),
                dataset_version_id=row.dataset_version_id,
                entity_id=row.entity_id,
                series_id=row.series_id,
                observation_selector={
                    "timestamp": timestamp,
                    "quality_flag": row.quality_flag,
                },
                claim_text=f"{row.entity_name} registrou {value} {row.unit} em {timestamp} para {row.metric_name}.",
            )
            session.add(evidence)

    def observation_scope_id(self, series_id: str, entity_id: str, timestamp: str) -> str:
        return f"{series_id}:{entity_id}:{timestamp}"


evidence_service = EvidenceService()

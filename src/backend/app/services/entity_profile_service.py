from __future__ import annotations

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    AgentProfileMaster,
    AssetBridgeGeneration,
    AssetMasterGeneration,
    Dataset,
    DatasetVersion,
    Entity,
    EntityAlias,
    EvidenceRegistry,
    GeoElectricMaster,
    MetricSeries,
    Observation,
    PartyMaster,
    Relation,
    SeriesRegistry,
    Source,
)
from app.services.catalog_service import to_iso8601
from app.services.graph_service import GraphBackendUnavailable, get_graph_service


class EntityProfileService:
    def get_profile(self, session: Session, entity_id: str) -> dict[str, object] | None:
        entity = session.get(Entity, entity_id)
        if entity is None:
            return None

        aliases = session.execute(
            select(
                EntityAlias.alias_name,
                EntityAlias.external_code,
                EntityAlias.confidence,
                Source.code.label("source_code"),
            )
            .join(Source, Source.id == EntityAlias.source_id)
            .where(EntityAlias.entity_id == entity_id)
            .order_by(Source.code, EntityAlias.alias_name)
        ).all()

        party = session.get(PartyMaster, entity_id)
        agent_profiles = session.scalars(
            select(AgentProfileMaster)
            .where(AgentProfileMaster.entity_id == entity_id)
            .order_by(AgentProfileMaster.profile_kind, AgentProfileMaster.role)
        ).all()
        generation_asset = session.get(AssetMasterGeneration, entity_id)
        generation_bridges = session.scalars(
            select(AssetBridgeGeneration)
            .where(AssetBridgeGeneration.asset_entity_id == entity_id)
            .order_by(AssetBridgeGeneration.bridge_kind, AssetBridgeGeneration.source_code)
        ).all()
        geo_records = session.scalars(
            select(GeoElectricMaster).where(GeoElectricMaster.entity_id == entity_id).order_by(GeoElectricMaster.geo_type)
        ).all()

        series_rows = session.execute(
            select(
                MetricSeries.id.label("series_id"),
                MetricSeries.dataset_id,
                Dataset.code.label("dataset_code"),
                MetricSeries.metric_code,
                MetricSeries.metric_name,
                MetricSeries.unit,
                MetricSeries.temporal_granularity,
                MetricSeries.latest_observation_at,
                SeriesRegistry.semantic_value_type,
                SeriesRegistry.reference_time_kind,
                Observation.value_numeric,
                Observation.value_text,
            )
            .join(Dataset, Dataset.id == MetricSeries.dataset_id)
            .join(Observation, Observation.series_id == MetricSeries.id)
            .outerjoin(SeriesRegistry, SeriesRegistry.metric_series_id == MetricSeries.id)
            .where(Observation.entity_id == entity_id)
            .order_by(MetricSeries.metric_name, Observation.time.desc())
        ).all()

        latest_by_series: dict[str, dict[str, object]] = {}
        for row in series_rows:
            if row.series_id in latest_by_series:
                continue
            latest_by_series[row.series_id] = {
                "series_id": row.series_id,
                "dataset_id": row.dataset_id,
                "dataset_code": row.dataset_code,
                "metric_code": row.metric_code,
                "metric_name": row.metric_name,
                "unit": row.unit,
                "temporal_granularity": row.temporal_granularity,
                "semantic_value_type": row.semantic_value_type or "observed",
                "reference_time_kind": row.reference_time_kind or "instant",
                "latest_observation_at": to_iso8601(row.latest_observation_at) or "",
                "latest_value": row.value_numeric if row.value_numeric is not None else row.value_text,
            }

        recent_versions = session.execute(
            select(
                distinct(DatasetVersion.id),
                DatasetVersion.label,
                DatasetVersion.published_at,
                Dataset.id.label("dataset_id"),
                Dataset.code.label("dataset_code"),
            )
            .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
            .join(Observation, Observation.dataset_version_id == DatasetVersion.id)
            .where(Observation.entity_id == entity_id)
            .order_by(DatasetVersion.published_at.desc())
            .limit(8)
        ).all()
        if not recent_versions:
            recent_versions = session.execute(
                select(
                    distinct(DatasetVersion.id),
                    DatasetVersion.label,
                    DatasetVersion.published_at,
                    Dataset.id.label("dataset_id"),
                    Dataset.code.label("dataset_code"),
                )
                .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
                .join(Relation, Relation.dataset_version_id == DatasetVersion.id)
                .where(or_(Relation.source_entity_id == entity_id, Relation.target_entity_id == entity_id))
                .order_by(DatasetVersion.published_at.desc())
                .limit(8)
            ).all()
        if not recent_versions:
            recent_versions = session.execute(
                select(
                    distinct(DatasetVersion.id),
                    DatasetVersion.label,
                    DatasetVersion.published_at,
                    Dataset.id.label("dataset_id"),
                    Dataset.code.label("dataset_code"),
                )
                .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
                .join(EvidenceRegistry, EvidenceRegistry.dataset_version_id == DatasetVersion.id)
                .where(EvidenceRegistry.entity_id == entity_id)
                .order_by(DatasetVersion.published_at.desc())
                .limit(8)
            ).all()

        evidence_rows = session.execute(
            select(
                EvidenceRegistry.id,
                EvidenceRegistry.scope_type,
                EvidenceRegistry.scope_id,
                EvidenceRegistry.dataset_version_id,
                EvidenceRegistry.series_id,
                EvidenceRegistry.observation_selector,
                EvidenceRegistry.claim_text,
                EvidenceRegistry.created_at,
            )
            .where(EvidenceRegistry.entity_id == entity_id)
            .order_by(EvidenceRegistry.created_at.desc())
            .limit(10)
        ).all()

        graph_status = "available"
        neighbors: dict[str, object] | None = None
        try:
            neighbors = get_graph_service().get_neighbors(session, entity_id)
        except GraphBackendUnavailable:
            graph_status = "unavailable"

        regulatory = None
        if entity.entity_type == "distributor":
            tracked_metrics = session.scalars(
                select(MetricSeries.metric_code)
                .join(Observation, Observation.series_id == MetricSeries.id)
                .where(Observation.entity_id == entity_id)
                .distinct()
                .order_by(MetricSeries.metric_code)
            ).all()
            regulatory = {
                "tracked_metrics": tracked_metrics,
                "observation_count": session.scalar(
                    select(func.count()).select_from(Observation).where(Observation.entity_id == entity_id)
                )
                or 0,
            }

        generation_asset_payload = None
        if generation_asset is not None:
            generation_asset_payload = {
                "ceg": generation_asset.ceg,
                "ons_plant_code": generation_asset.ons_plant_code,
                "source_type": generation_asset.source_type,
                "fuel_type": generation_asset.fuel_type,
                "installed_capacity_mw": generation_asset.installed_capacity_mw,
                "status": generation_asset.status,
                "municipality_entity_id": generation_asset.municipality_entity_id,
                "subsystem_entity_id": generation_asset.subsystem_entity_id,
                "submarket_entity_id": generation_asset.submarket_entity_id,
                "bridge_codes": [
                    {
                        "bridge_kind": bridge.bridge_kind,
                        "external_code": bridge.external_code,
                        "source_code": bridge.source_code,
                    }
                    for bridge in generation_bridges
                ],
            }

        return {
            "identity": {
                "id": entity.id,
                "entity_type": entity.entity_type,
                "canonical_code": entity.canonical_code or "",
                "name": entity.name,
                "jurisdiction": entity.jurisdiction,
                "attributes": dict(entity.attributes),
            },
            "aliases": [
                {
                    "source_code": row.source_code,
                    "alias_name": row.alias_name,
                    "external_code": row.external_code,
                    "confidence": row.confidence,
                }
                for row in aliases
            ],
            "semantic_type": entity.entity_type,
            "facets": {
                "party": {
                    "tax_id": party.tax_id,
                    "legal_name": party.legal_name,
                    "trade_name": party.trade_name,
                    "status": party.status,
                }
                if party is not None
                else None,
                "agent_profile": [
                    {
                        "profile_kind": profile.profile_kind,
                        "role": profile.role,
                        "source_code": profile.source_code,
                        "external_code": profile.external_code,
                        "valid_from": to_iso8601(profile.valid_from),
                        "valid_to": to_iso8601(profile.valid_to),
                    }
                    for profile in agent_profiles
                ],
                "generation_asset": generation_asset_payload,
                "geo": [
                    {
                        "geo_type": record.geo_type,
                        "ibge_code": record.ibge_code,
                        "operator_code": record.operator_code,
                        "parent_entity_id": record.parent_entity_id,
                        "mapped_entity_id": record.mapped_entity_id,
                    }
                    for record in geo_records
                ],
                "regulatory": regulatory,
            },
            "series": list(latest_by_series.values()),
            "neighbors": neighbors,
            "recent_versions": [
                {
                    "dataset_version_id": row[0],
                    "label": row[1],
                    "published_at": to_iso8601(row[2]),
                    "dataset_id": row[3],
                    "dataset_code": row[4],
                }
                for row in recent_versions
            ],
            "evidence": [
                {
                    "id": row.id,
                    "scope_type": row.scope_type,
                    "scope_id": row.scope_id,
                    "dataset_version_id": row.dataset_version_id,
                    "series_id": row.series_id,
                    "selector": dict(row.observation_selector or {}),
                    "claim_text": row.claim_text,
                    "created_at": to_iso8601(row.created_at),
                }
                for row in evidence_rows
            ],
            "graph_status": graph_status,
        }


entity_profile_service = EntityProfileService()

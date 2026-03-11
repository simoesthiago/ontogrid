from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AgentProfileMaster,
    AssetBridgeGeneration,
    AssetMasterGeneration,
    Dataset,
    DatasetVersion,
    Entity,
    GeoElectricMaster,
    PartyMaster,
    SeriesRegistry,
)
from app.ingestion.base import ParsedDatasetPayload, ParsedEntity, ParsedEntityAlias


class SemanticService:
    def persist_payload_semantics(
        self,
        session: Session,
        dataset: Dataset,
        version: DatasetVersion,
        payload: ParsedDatasetPayload,
        entity_ids_by_key: dict[str, str],
        series_ids_by_key: dict[str, str],
    ) -> None:
        aliases_by_entity_key = self._group_aliases(payload.aliases)

        for parsed_series in payload.metric_series:
            series_id = series_ids_by_key.get(parsed_series.key)
            if series_id is None:
                continue
            registry = session.get(SeriesRegistry, series_id)
            if registry is None:
                registry = SeriesRegistry(metric_series_id=series_id)
                session.add(registry)
            registry.semantic_value_type = parsed_series.semantic_value_type
            registry.reference_time_kind = parsed_series.reference_time_kind
            registry.target_entity_type = parsed_series.entity_type
            registry.unit = parsed_series.unit
            registry.source_dataset_version_id = version.id

        for parsed_entity in payload.entities:
            entity_id = entity_ids_by_key.get(parsed_entity.key)
            if entity_id is None:
                continue
            aliases = aliases_by_entity_key.get(parsed_entity.key, [])
            self._upsert_party_master(session, parsed_entity, entity_id, version.id)
            self._upsert_agent_profile_master(session, parsed_entity, entity_id, aliases, version.id)
            self._upsert_asset_master_generation(session, parsed_entity, entity_ids_by_key, entity_id, version.id)
            self._upsert_asset_bridges(session, parsed_entity, aliases, entity_id, dataset.source.code if dataset.source else "", version.id)
            self._upsert_geo_records(session, parsed_entity, entity_ids_by_key, entity_id, version.id)

    def _group_aliases(self, aliases: list[ParsedEntityAlias]) -> dict[str, list[ParsedEntityAlias]]:
        grouped: dict[str, list[ParsedEntityAlias]] = {}
        for alias in aliases:
            grouped.setdefault(alias.entity_key, []).append(alias)
        return grouped

    def _upsert_party_master(
        self,
        session: Session,
        parsed_entity: ParsedEntity,
        entity_id: str,
        dataset_version_id: str,
    ) -> None:
        if parsed_entity.entity_type not in {"agent", "distributor"}:
            return
        tax_id = str(parsed_entity.attributes.get("tax_id", "")).strip() or None
        legal_name = str(parsed_entity.attributes.get("legal_name") or parsed_entity.name)
        trade_name = str(parsed_entity.attributes.get("trade_name") or "").strip() or None
        status = str(parsed_entity.attributes.get("status") or "active")

        party = session.get(PartyMaster, entity_id)
        if party is None:
            party = PartyMaster(entity_id=entity_id, legal_name=legal_name, status=status, source_dataset_version_id=dataset_version_id)
            session.add(party)
        party.tax_id = tax_id
        party.legal_name = legal_name
        party.trade_name = trade_name
        party.status = status
        party.source_dataset_version_id = dataset_version_id
        party.lineage = {
            "entity_type": parsed_entity.entity_type,
            "canonical_code": parsed_entity.canonical_code,
        }

    def _upsert_agent_profile_master(
        self,
        session: Session,
        parsed_entity: ParsedEntity,
        entity_id: str,
        aliases: list[ParsedEntityAlias],
        dataset_version_id: str,
    ) -> None:
        if parsed_entity.entity_type not in {"agent", "distributor"}:
            return

        profile_kind = str(parsed_entity.attributes.get("profile_kind") or "sector")
        role = str(parsed_entity.attributes.get("role") or parsed_entity.entity_type)
        source_code = str(parsed_entity.attributes.get("source_code") or "")
        external_code = next(
            (
                alias.external_code
                for alias in aliases
                if alias.source_code == source_code and alias.external_code
            ),
            None,
        )

        profile = session.scalar(
            select(AgentProfileMaster).where(
                AgentProfileMaster.entity_id == entity_id,
                AgentProfileMaster.profile_kind == profile_kind,
                AgentProfileMaster.role == role,
                AgentProfileMaster.source_code == source_code,
                AgentProfileMaster.external_code == external_code,
            )
        )
        if profile is None:
            profile = AgentProfileMaster(
                id=str(uuid4()),
                entity_id=entity_id,
                party_entity_id=entity_id,
                profile_kind=profile_kind,
                role=role,
                source_code=source_code,
                external_code=external_code,
                source_dataset_version_id=dataset_version_id,
            )
            session.add(profile)
        profile.party_entity_id = entity_id
        profile.valid_from = self._coerce_datetime(parsed_entity.attributes.get("valid_from"))
        profile.valid_to = self._coerce_datetime(parsed_entity.attributes.get("valid_to"))
        profile.source_dataset_version_id = dataset_version_id

    def _upsert_asset_master_generation(
        self,
        session: Session,
        parsed_entity: ParsedEntity,
        entity_ids_by_key: dict[str, str],
        entity_id: str,
        dataset_version_id: str,
    ) -> None:
        if parsed_entity.entity_type != "plant":
            return

        asset = session.get(AssetMasterGeneration, entity_id)
        if asset is None:
            asset = AssetMasterGeneration(entity_id=entity_id, source_dataset_version_id=dataset_version_id)
            session.add(asset)
        asset.ceg = self._coerce_str(parsed_entity.attributes.get("ceg"))
        asset.ons_plant_code = self._coerce_str(parsed_entity.attributes.get("ons_plant_code"))
        asset.source_type = self._coerce_str(parsed_entity.attributes.get("source_type"))
        asset.fuel_type = self._coerce_str(parsed_entity.attributes.get("fuel_type"))
        asset.installed_capacity_mw = self._coerce_float(parsed_entity.attributes.get("installed_capacity_mw"))
        asset.status = self._coerce_str(parsed_entity.attributes.get("status")) or "active"
        asset.municipality_entity_id = entity_ids_by_key.get(self._coerce_str(parsed_entity.attributes.get("municipality_entity_key")) or "")
        asset.subsystem_entity_id = entity_ids_by_key.get(self._coerce_str(parsed_entity.attributes.get("subsystem_entity_key")) or "")
        asset.submarket_entity_id = entity_ids_by_key.get(self._coerce_str(parsed_entity.attributes.get("submarket_entity_key")) or "")
        asset.source_dataset_version_id = dataset_version_id

    def _upsert_asset_bridges(
        self,
        session: Session,
        parsed_entity: ParsedEntity,
        aliases: list[ParsedEntityAlias],
        entity_id: str,
        dataset_source_code: str,
        dataset_version_id: str,
    ) -> None:
        if parsed_entity.entity_type != "plant":
            return

        bridge_specs: list[tuple[str, str, str]] = []
        for bridge_kind, value in (
            ("ceg", parsed_entity.attributes.get("ceg")),
            ("ons_plant_code", parsed_entity.attributes.get("ons_plant_code")),
        ):
            bridge_value = self._coerce_str(value)
            if bridge_value:
                bridge_specs.append((bridge_kind, bridge_value, dataset_source_code))
        for alias in aliases:
            if alias.external_code:
                bridge_specs.append(("source_alias", alias.external_code, alias.source_code))

        for bridge_kind, external_code, source_code in bridge_specs:
            bridge = session.scalar(
                select(AssetBridgeGeneration).where(
                    AssetBridgeGeneration.asset_entity_id == entity_id,
                    AssetBridgeGeneration.bridge_kind == bridge_kind,
                    AssetBridgeGeneration.source_code == source_code,
                    AssetBridgeGeneration.external_code == external_code,
                )
            )
            if bridge is None:
                bridge = AssetBridgeGeneration(
                    id=str(uuid4()),
                    asset_entity_id=entity_id,
                    bridge_kind=bridge_kind,
                    external_code=external_code,
                    source_code=source_code,
                    source_dataset_version_id=dataset_version_id,
                )
                session.add(bridge)
            bridge.valid_from = self._coerce_datetime(parsed_entity.attributes.get("valid_from"))
            bridge.valid_to = self._coerce_datetime(parsed_entity.attributes.get("valid_to"))
            bridge.source_dataset_version_id = dataset_version_id

    def _upsert_geo_records(
        self,
        session: Session,
        parsed_entity: ParsedEntity,
        entity_ids_by_key: dict[str, str],
        entity_id: str,
        dataset_version_id: str,
    ) -> None:
        geo_type = parsed_entity.entity_type
        if geo_type in {"municipality", "submarket", "subsystem", "reservoir"}:
            mapped_id = entity_ids_by_key.get(self._coerce_str(parsed_entity.attributes.get("mapped_entity_key")) or "")
            parent_id = entity_ids_by_key.get(self._coerce_str(parsed_entity.attributes.get("parent_entity_key")) or "")
            self._upsert_geo_master(
                session,
                entity_id=entity_id,
                geo_type=geo_type,
                ibge_code=self._coerce_str(parsed_entity.attributes.get("ibge_code")),
                operator_code=parsed_entity.canonical_code,
                parent_entity_id=parent_id,
                mapped_entity_id=mapped_id,
                valid_from=self._coerce_datetime(parsed_entity.attributes.get("valid_from")),
                valid_to=self._coerce_datetime(parsed_entity.attributes.get("valid_to")),
                dataset_version_id=dataset_version_id,
            )

        for relation_name, geo_record_type in (
            ("municipality_entity_key", "municipality"),
            ("subsystem_entity_key", "subsystem"),
            ("submarket_entity_key", "submarket"),
        ):
            mapped_entity_id = entity_ids_by_key.get(self._coerce_str(parsed_entity.attributes.get(relation_name)) or "")
            if mapped_entity_id:
                self._upsert_geo_master(
                    session,
                    entity_id=entity_id,
                    geo_type=geo_record_type,
                    ibge_code=self._coerce_str(parsed_entity.attributes.get("ibge_code")) if geo_record_type == "municipality" else None,
                    operator_code=self._coerce_str(parsed_entity.attributes.get(f"{geo_record_type}_code")),
                    parent_entity_id=None,
                    mapped_entity_id=mapped_entity_id,
                    valid_from=self._coerce_datetime(parsed_entity.attributes.get("valid_from")),
                    valid_to=self._coerce_datetime(parsed_entity.attributes.get("valid_to")),
                    dataset_version_id=dataset_version_id,
                )

    def _upsert_geo_master(
        self,
        session: Session,
        *,
        entity_id: str,
        geo_type: str,
        ibge_code: str | None,
        operator_code: str | None,
        parent_entity_id: str | None,
        mapped_entity_id: str | None,
        valid_from: datetime | None,
        valid_to: datetime | None,
        dataset_version_id: str,
    ) -> None:
        record = session.scalar(
            select(GeoElectricMaster).where(
                GeoElectricMaster.entity_id == entity_id,
                GeoElectricMaster.geo_type == geo_type,
                GeoElectricMaster.mapped_entity_id == mapped_entity_id,
            )
        )
        if record is None:
            record = GeoElectricMaster(
                id=str(uuid4()),
                entity_id=entity_id,
                geo_type=geo_type,
                source_dataset_version_id=dataset_version_id,
            )
            session.add(record)
        record.ibge_code = ibge_code
        record.operator_code = operator_code
        record.parent_entity_id = parent_entity_id
        record.mapped_entity_id = mapped_entity_id
        record.valid_from = valid_from
        record.valid_to = valid_to
        record.source_dataset_version_id = dataset_version_id

    def _coerce_datetime(self, value: object) -> datetime | None:
        if isinstance(value, datetime):
            return value
        return None

    def _coerce_str(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _coerce_float(self, value: object) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


semantic_service = SemanticService()

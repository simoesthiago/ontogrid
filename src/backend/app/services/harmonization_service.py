from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AssetMasterGeneration, Entity, EntityAlias, HarmonizationEvent, PartyMaster, Source
from app.ingestion.adapters.common import normalize_lookup, normalize_token
from app.ingestion.base import ParsedEntity, ParsedEntityAlias


@dataclass
class HarmonizationResult:
    entity: Entity
    decision: str
    match_rule: str
    matched_on: dict[str, object]
    source_identity: dict[str, object]


class HarmonizationService:
    def upsert_entity(
        self,
        session: Session,
        *,
        source: Source,
        dataset_version_id: str,
        parsed_entity: ParsedEntity,
        aliases: list[ParsedEntityAlias],
        seen_at: datetime,
    ) -> HarmonizationResult:
        entity, match_rule, matched_on = self._resolve_match(session, source, parsed_entity, aliases)
        decision = "matched_existing" if entity is not None else "created_new"
        if entity is None:
            entity = Entity(
                id=str(uuid4()),
                entity_type=parsed_entity.entity_type,
                canonical_code=parsed_entity.canonical_code,
                name=parsed_entity.name,
                jurisdiction=parsed_entity.jurisdiction,
                attributes=dict(parsed_entity.attributes),
                first_seen_at=seen_at,
                last_seen_at=seen_at,
            )
            session.add(entity)
            session.flush()
        else:
            entity.canonical_code = entity.canonical_code or parsed_entity.canonical_code
            entity.name = parsed_entity.name
            entity.jurisdiction = parsed_entity.jurisdiction
            entity.attributes = {**entity.attributes, **dict(parsed_entity.attributes)}
            entity.last_seen_at = seen_at

        source_identity = self._build_source_identity(source.code, parsed_entity, aliases)
        self._record_event(
            session,
            dataset_version_id=dataset_version_id,
            entity=entity,
            source_code=source.code,
            source_record_key=parsed_entity.key,
            decision=decision,
            match_rule=match_rule,
            matched_on=matched_on,
            source_identity=source_identity,
        )
        return HarmonizationResult(
            entity=entity,
            decision=decision,
            match_rule=match_rule,
            matched_on=matched_on,
            source_identity=source_identity,
        )

    def _resolve_match(
        self,
        session: Session,
        source: Source,
        parsed_entity: ParsedEntity,
        aliases: list[ParsedEntityAlias],
    ) -> tuple[Entity | None, str, dict[str, object]]:
        if parsed_entity.entity_type in {"agent", "distributor"}:
            return self._match_party(session, source, parsed_entity, aliases)
        if parsed_entity.entity_type == "plant":
            return self._match_plant(session, source, parsed_entity)
        if parsed_entity.entity_type in {"municipality", "subsystem", "submarket", "reservoir"}:
            return self._match_geo_electric(session, parsed_entity)
        return self._match_generic(session, parsed_entity)

    def _match_party(
        self,
        session: Session,
        source: Source,
        parsed_entity: ParsedEntity,
        aliases: list[ParsedEntityAlias],
    ) -> tuple[Entity | None, str, dict[str, object]]:
        tax_id = self._normalized_tax_id(parsed_entity.attributes.get("tax_id"))
        if tax_id:
            entity = session.scalar(
                select(Entity)
                .join(PartyMaster, PartyMaster.entity_id == Entity.id)
                .where(Entity.entity_type == parsed_entity.entity_type, PartyMaster.tax_id == tax_id)
            )
            if entity is not None:
                return entity, "exact_tax_id", {"tax_id": tax_id}

        external_codes = sorted(
            {
                code
                for code in (
                    self._normalized_identifier(alias.external_code)
                    for alias in aliases
                    if alias.source_code == source.code
                )
                if code
            }
        )
        if external_codes:
            entity = session.scalar(
                select(Entity)
                .join(EntityAlias, EntityAlias.entity_id == Entity.id)
                .where(
                    Entity.entity_type == parsed_entity.entity_type,
                    EntityAlias.source_id == source.id,
                    EntityAlias.external_code.in_(external_codes),
                )
            )
            if entity is not None:
                return entity, "source_external_code", {"source_code": source.code, "external_codes": external_codes}

        normalized_legal_name = self._normalized_name(parsed_entity.attributes.get("legal_name") or parsed_entity.name)
        if normalized_legal_name:
            for entity, party in session.execute(
                select(Entity, PartyMaster)
                .outerjoin(PartyMaster, PartyMaster.entity_id == Entity.id)
                .where(Entity.entity_type == parsed_entity.entity_type)
            ).all():
                candidate_name = self._normalized_name((party.legal_name if party is not None else entity.name))
                if candidate_name == normalized_legal_name:
                    return entity, "exact_normalized_legal_name", {"legal_name": normalized_legal_name}
        return None, "created_new", {"reason": "no_exact_public_match"}

    def _match_plant(
        self,
        session: Session,
        source: Source,
        parsed_entity: ParsedEntity,
    ) -> tuple[Entity | None, str, dict[str, object]]:
        ceg = self._normalized_identifier(parsed_entity.attributes.get("ceg"))
        if ceg:
            entity = session.scalar(
                select(Entity)
                .join(AssetMasterGeneration, AssetMasterGeneration.entity_id == Entity.id)
                .where(Entity.entity_type == "plant", AssetMasterGeneration.ceg == ceg)
            )
            if entity is not None:
                return entity, "exact_ceg", {"ceg": ceg}

        ons_plant_code = self._normalized_identifier(parsed_entity.attributes.get("ons_plant_code"))
        if ons_plant_code:
            entity = session.scalar(
                select(Entity)
                .join(AssetMasterGeneration, AssetMasterGeneration.entity_id == Entity.id)
                .where(Entity.entity_type == "plant", AssetMasterGeneration.ons_plant_code == ons_plant_code)
            )
            if entity is not None:
                return entity, "exact_ons_plant_code", {"ons_plant_code": ons_plant_code}

        normalized_name = self._normalized_name(parsed_entity.name)
        source_code = str(parsed_entity.attributes.get("source_code") or source.code)
        if normalized_name and parsed_entity.jurisdiction:
            for entity in session.scalars(
                select(Entity).where(Entity.entity_type == "plant", Entity.jurisdiction == parsed_entity.jurisdiction)
            ).all():
                candidate_name = self._normalized_name(entity.name)
                candidate_source_code = str(entity.attributes.get("source_code") or "")
                if candidate_name == normalized_name and candidate_source_code == source_code:
                    return entity, "exact_name_jurisdiction_primary_source", {
                        "name": normalized_name,
                        "jurisdiction": parsed_entity.jurisdiction,
                        "source_code": source_code,
                    }
        return None, "created_new", {"reason": "no_exact_public_match"}

    def _match_geo_electric(
        self,
        session: Session,
        parsed_entity: ParsedEntity,
    ) -> tuple[Entity | None, str, dict[str, object]]:
        if parsed_entity.entity_type == "municipality":
            ibge_code = self._normalized_identifier(parsed_entity.attributes.get("ibge_code"))
            if ibge_code:
                for entity in session.scalars(select(Entity).where(Entity.entity_type == "municipality")).all():
                    if self._normalized_identifier(entity.attributes.get("ibge_code")) == ibge_code:
                        return entity, "exact_ibge_code", {"ibge_code": ibge_code}

        operator_code = self._normalized_identifier(
            parsed_entity.attributes.get("operator_code") or parsed_entity.canonical_code
        )
        if operator_code:
            entity = session.scalar(
                select(Entity).where(
                    Entity.entity_type == parsed_entity.entity_type,
                    Entity.canonical_code == operator_code,
                )
            )
            if entity is not None:
                return entity, "exact_operator_code", {"operator_code": operator_code}
        return self._match_generic(session, parsed_entity)

    def _match_generic(self, session: Session, parsed_entity: ParsedEntity) -> tuple[Entity | None, str, dict[str, object]]:
        if parsed_entity.canonical_code:
            entity = session.scalar(
                select(Entity).where(
                    Entity.entity_type == parsed_entity.entity_type,
                    Entity.canonical_code == parsed_entity.canonical_code,
                )
            )
            if entity is not None:
                return entity, "exact_canonical_code", {"canonical_code": parsed_entity.canonical_code}

        normalized_name = self._normalized_name(parsed_entity.name)
        if normalized_name:
            for entity in session.scalars(select(Entity).where(Entity.entity_type == parsed_entity.entity_type)).all():
                if self._normalized_name(entity.name) == normalized_name:
                    return entity, "exact_normalized_name", {"name": normalized_name}
        return None, "created_new", {"reason": "no_exact_public_match"}

    def _record_event(
        self,
        session: Session,
        *,
        dataset_version_id: str,
        entity: Entity,
        source_code: str,
        source_record_key: str,
        decision: str,
        match_rule: str,
        matched_on: dict[str, object],
        source_identity: dict[str, object],
    ) -> None:
        existing = session.scalar(
            select(HarmonizationEvent).where(
                HarmonizationEvent.dataset_version_id == dataset_version_id,
                HarmonizationEvent.source_record_key == source_record_key,
            )
        )
        if existing is None:
            existing = HarmonizationEvent(
                id=str(uuid4()),
                dataset_version_id=dataset_version_id,
                entity_id=entity.id,
                source_code=source_code,
                entity_type=entity.entity_type,
                source_record_key=source_record_key,
            )
            session.add(existing)
        existing.entity_id = entity.id
        existing.source_code = source_code
        existing.entity_type = entity.entity_type
        existing.decision = decision
        existing.match_rule = match_rule
        existing.matched_on = matched_on
        existing.source_identity = source_identity

    def _build_source_identity(
        self,
        source_code: str,
        parsed_entity: ParsedEntity,
        aliases: list[ParsedEntityAlias],
    ) -> dict[str, object]:
        return {
            "source_code": source_code,
            "entity_key": parsed_entity.key,
            "entity_type": parsed_entity.entity_type,
            "canonical_code": parsed_entity.canonical_code,
            "name": parsed_entity.name,
            "jurisdiction": parsed_entity.jurisdiction,
            "attributes": dict(parsed_entity.attributes),
            "aliases": [
                {
                    "source_code": alias.source_code,
                    "alias_name": alias.alias_name,
                    "external_code": alias.external_code,
                }
                for alias in aliases
            ],
        }

    def _normalized_name(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        return normalize_lookup(text)

    def _normalized_identifier(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        return normalize_token(text).upper()

    def _normalized_tax_id(self, value: object) -> str | None:
        if value is None:
            return None
        digits = re.sub(r"[^0-9]", "", str(value))
        return digits or None


harmonization_service = HarmonizationService()

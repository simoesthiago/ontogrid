from __future__ import annotations

from app.ingestion.adapters.common import (
    agent_code,
    canonical_submarket,
    municipality_code,
    normalize_token,
    plant_code,
    subsystem_code,
)
from app.ingestion.base import (
    CkanDatasetAdapter,
    ParsedDatasetPayload,
    ParsedDatasetVersion,
    ParsedEntity,
    ParsedEntityAlias,
    ParsedMetricSeries,
    ParsedObservation,
    ParsedRelation,
)


class OnsCargaAdapter(CkanDatasetAdapter):
    dataset_code = "carga_horaria_submercado"
    source_code = "ons"
    fixture_name = "ons_carga_horaria_submercado.csv"
    settings_url_field = "ons_carga_url"
    ckan_base_url_field = "ons_ckan_base_url"
    ckan_package_id_field = "ons_carga_package_id"
    ckan_resource_id_field = "ons_carga_resource_id"
    prefer_datastore = True

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        timestamps = [self.parse_datetime(row["timestamp"]) for row in rows]
        published_at = max(timestamps)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        observations: list[ParsedObservation] = []
        for row in rows:
            entity_timestamp = self.parse_datetime(row["timestamp"])
            submarket_code, submarket_name = canonical_submarket(row["submarket"])
            entity_key = f"submarket:{submarket_code}"
            entities_by_key.setdefault(
                entity_key,
                ParsedEntity(
                    key=entity_key,
                    entity_type="submarket",
                    canonical_code=submarket_code,
                    name=submarket_name,
                    jurisdiction="SIN",
                    attributes={
                        "source_dataset": self.dataset_code,
                        "source_code": self.source_code,
                        "operator_code": submarket_code,
                    },
                ),
            )
            aliases_by_key.setdefault(
                (entity_key, row["submarket"]),
                ParsedEntityAlias(
                    entity_key=entity_key,
                    source_code=self.source_code,
                    alias_name=row["submarket"],
                    external_code=normalize_token(row["submarket"]).upper(),
                    confidence=1.0,
                ),
            )
            observations.append(
                ParsedObservation(
                    series_key="series:load_mw",
                    entity_key=entity_key,
                    time=entity_timestamp,
                    value_numeric=float(row["load_mw"]),
                    published_at=published_at,
                )
            )

        version = ParsedDatasetVersion(
            label=published_at.date().isoformat(),
            extracted_at=published_at,
            published_at=published_at,
            coverage_start=min(timestamps),
            coverage_end=max(timestamps),
            row_count=len(rows),
            schema_version="v1",
            checksum=checksum,
        )
        return ParsedDatasetPayload(
            dataset_version=version,
            entities=list(entities_by_key.values()),
            aliases=list(aliases_by_key.values()),
            metric_series=[
                ParsedMetricSeries(
                    key="series:load_mw",
                    metric_code="load_mw",
                    metric_name="Carga",
                    unit="MW",
                    temporal_granularity="hour",
                    entity_type="submarket",
                    semantic_value_type="observed",
                    reference_time_kind="instant",
                    dimensions={"source": "ons"},
                )
            ],
            observations=observations,
        )


class OnsCargaDiariaAdapter(CkanDatasetAdapter):
    dataset_code = "carga_energia_diaria"
    source_code = "ons"
    fixture_name = "ons_carga_energia_diaria.csv"
    settings_url_field = "ons_carga_diaria_url"
    ckan_base_url_field = "ons_ckan_base_url"
    ckan_package_id_field = "ons_carga_diaria_package_id"
    ckan_resource_id_field = "ons_carga_diaria_resource_id"
    prefer_datastore = True

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        timestamps = [self.parse_datetime(row["date"]) for row in rows]
        published_at = max(timestamps)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        observations: list[ParsedObservation] = []
        for row in rows:
            entity_timestamp = self.parse_datetime(row["date"])
            submarket_code, submarket_name = canonical_submarket(row["submarket"])
            entity_key = f"submarket:{submarket_code}"
            entities_by_key.setdefault(
                entity_key,
                ParsedEntity(
                    key=entity_key,
                    entity_type="submarket",
                    canonical_code=submarket_code,
                    name=submarket_name,
                    jurisdiction="SIN",
                    attributes={
                        "source_dataset": self.dataset_code,
                        "source_code": self.source_code,
                        "operator_code": submarket_code,
                    },
                ),
            )
            aliases_by_key.setdefault(
                (entity_key, row["submarket"]),
                ParsedEntityAlias(
                    entity_key=entity_key,
                    source_code=self.source_code,
                    alias_name=row["submarket"],
                    external_code=normalize_token(row["submarket"]).upper(),
                    confidence=1.0,
                ),
            )
            observations.append(
                ParsedObservation(
                    series_key="series:load_avg_mw",
                    entity_key=entity_key,
                    time=entity_timestamp,
                    value_numeric=float(row["load_avg_mw"]),
                    published_at=published_at,
                )
            )

        version = ParsedDatasetVersion(
            label=published_at.date().isoformat(),
            extracted_at=published_at,
            published_at=published_at,
            coverage_start=min(timestamps),
            coverage_end=max(timestamps),
            row_count=len(rows),
            schema_version="v1",
            checksum=checksum,
        )
        return ParsedDatasetPayload(
            dataset_version=version,
            entities=list(entities_by_key.values()),
            aliases=list(aliases_by_key.values()),
            metric_series=[
                ParsedMetricSeries(
                    key="series:load_avg_mw",
                    metric_code="load_avg_mw",
                    metric_name="Carga media diaria",
                    unit="MWmed",
                    temporal_granularity="day",
                    entity_type="submarket",
                    semantic_value_type="observed",
                    reference_time_kind="instant",
                    dimensions={"source": "ons"},
                )
            ],
            observations=observations,
        )


class OnsGeracaoUsinaAdapter(CkanDatasetAdapter):
    dataset_code = "geracao_usina_horaria"
    source_code = "ons"
    fixture_name = "ons_geracao_usina_horaria.csv"
    settings_url_field = "ons_geracao_usina_url"
    ckan_base_url_field = "ons_ckan_base_url"
    ckan_package_id_field = "ons_geracao_usina_package_id"
    ckan_resource_id_field = "ons_geracao_usina_resource_id"
    prefer_datastore = True

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        timestamps = [self.parse_datetime(row["timestamp"]) for row in rows]
        published_at = max(timestamps)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        relations: dict[tuple[str, str, str], ParsedRelation] = {}
        observations: list[ParsedObservation] = []

        for row in rows:
            observation_time = self.parse_datetime(row["timestamp"])
            submarket_code, submarket_name = canonical_submarket(row["submarket"])
            subsystem_name = row.get("subsystem") or submarket_name
            subsystem_id = subsystem_code(subsystem_name)
            municipality_name = row.get("municipality", "").strip()
            municipality_ibge = row.get("ibge_code", "").strip()
            municipality_id = municipality_code(municipality_name, municipality_ibge) if municipality_name else None
            plant_id = plant_code(row["plant_name"], ceg=row.get("ceg"), ons_plant_code=row.get("ons_plant_code"))
            plant_key = f"plant:{plant_id}"
            agent_id = agent_code(row["agent_name"], row.get("agent_cnpj"))
            agent_key = f"agent:{agent_id}"
            submarket_key = f"submarket:{submarket_code}"
            subsystem_key = f"subsystem:{subsystem_id}"
            municipality_key = f"municipality:{municipality_id}" if municipality_id else None

            entities_by_key.setdefault(
                agent_key,
                ParsedEntity(
                    key=agent_key,
                    entity_type="agent",
                    canonical_code=agent_id,
                    name=row["agent_name"].strip(),
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={
                        "tax_id": row.get("agent_cnpj", "").strip() or None,
                        "legal_name": row["agent_name"].strip(),
                        "profile_kind": "sector",
                        "role": "generator",
                        "source_code": self.source_code,
                        "status": "active",
                    },
                ),
            )
            aliases_by_key.setdefault(
                (agent_key, row["agent_name"]),
                ParsedEntityAlias(
                    entity_key=agent_key,
                    source_code=self.source_code,
                    alias_name=row["agent_name"].strip(),
                    external_code=row.get("agent_cnpj", "").strip() or agent_id,
                    confidence=1.0,
                ),
            )

            if municipality_key:
                entities_by_key.setdefault(
                    municipality_key,
                    ParsedEntity(
                        key=municipality_key,
                        entity_type="municipality",
                        canonical_code=municipality_id,
                        name=municipality_name,
                        jurisdiction=row.get("state", "BR") or "BR",
                        attributes={
                            "ibge_code": municipality_ibge or None,
                            "source_code": self.source_code,
                        },
                    ),
                )

            entities_by_key.setdefault(
                submarket_key,
                ParsedEntity(
                    key=submarket_key,
                    entity_type="submarket",
                    canonical_code=submarket_code,
                    name=submarket_name,
                    jurisdiction="SIN",
                    attributes={"source_code": self.source_code, "operator_code": submarket_code},
                ),
            )
            entities_by_key.setdefault(
                subsystem_key,
                ParsedEntity(
                    key=subsystem_key,
                    entity_type="subsystem",
                    canonical_code=subsystem_id,
                    name=subsystem_name.strip(),
                    jurisdiction="SIN",
                    attributes={"source_code": self.source_code, "operator_code": subsystem_id},
                ),
            )
            entities_by_key.setdefault(
                plant_key,
                ParsedEntity(
                    key=plant_key,
                    entity_type="plant",
                    canonical_code=plant_id,
                    name=row["plant_name"].strip(),
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={
                        "ceg": row.get("ceg", "").strip() or None,
                        "ons_plant_code": row.get("ons_plant_code", "").strip() or None,
                        "source_type": row.get("source_type", "").strip() or None,
                        "fuel_type": row.get("fuel_type", "").strip() or None,
                        "status": row.get("status", "operating").strip() or "operating",
                        "municipality_entity_key": municipality_key,
                        "submarket_entity_key": submarket_key,
                        "subsystem_entity_key": subsystem_key,
                        "source_code": self.source_code,
                    },
                ),
            )
            aliases_by_key.setdefault(
                (plant_key, row["plant_name"]),
                ParsedEntityAlias(
                    entity_key=plant_key,
                    source_code=self.source_code,
                    alias_name=row["plant_name"].strip(),
                    external_code=row.get("ons_plant_code", "").strip() or row.get("ceg", "").strip() or plant_id,
                    confidence=1.0,
                ),
            )

            relations[(plant_key, agent_key, "OPERATED_BY")] = ParsedRelation(
                relation_type="OPERATED_BY",
                source_entity_key=plant_key,
                target_entity_key=agent_key,
            )
            relations[(plant_key, subsystem_key, "BELONGS_TO_SUBSYSTEM")] = ParsedRelation(
                relation_type="BELONGS_TO_SUBSYSTEM",
                source_entity_key=plant_key,
                target_entity_key=subsystem_key,
            )
            relations[(plant_key, submarket_key, "MAPPED_TO_SUBMARKET")] = ParsedRelation(
                relation_type="MAPPED_TO_SUBMARKET",
                source_entity_key=plant_key,
                target_entity_key=submarket_key,
            )
            if municipality_key:
                relations[(plant_key, municipality_key, "LOCATED_IN")] = ParsedRelation(
                    relation_type="LOCATED_IN",
                    source_entity_key=plant_key,
                    target_entity_key=municipality_key,
                )

            observations.append(
                ParsedObservation(
                    series_key="series:generation_mw",
                    entity_key=plant_key,
                    time=observation_time,
                    value_numeric=float(row["generation_mw"]),
                    published_at=published_at,
                )
            )

        version = ParsedDatasetVersion(
            label=published_at.date().isoformat(),
            extracted_at=published_at,
            published_at=published_at,
            coverage_start=min(timestamps),
            coverage_end=max(timestamps),
            row_count=len(rows),
            schema_version="v1",
            checksum=checksum,
        )
        return ParsedDatasetPayload(
            dataset_version=version,
            entities=list(entities_by_key.values()),
            aliases=list(aliases_by_key.values()),
            relations=list(relations.values()),
            metric_series=[
                ParsedMetricSeries(
                    key="series:generation_mw",
                    metric_code="generation_mw",
                    metric_name="Geracao verificada",
                    unit="MW",
                    temporal_granularity="hour",
                    entity_type="plant",
                    semantic_value_type="observed",
                    reference_time_kind="instant",
                    dimensions={"source": "ons"},
                )
            ],
            observations=observations,
        )

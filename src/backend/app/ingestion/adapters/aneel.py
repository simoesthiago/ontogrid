from __future__ import annotations

from app.ingestion.adapters.common import agent_code, canonical_submarket, distributor_code, municipality_code, plant_code
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


class AneelTarifasAdapter(CkanDatasetAdapter):
    dataset_code = "tarifas_distribuicao"
    source_code = "aneel"
    fixture_name = "aneel_tarifas_distribuicao.csv"
    settings_url_field = "aneel_tarifas_url"
    ckan_base_url_field = "aneel_ckan_base_url"
    ckan_package_id_field = "aneel_tarifas_package_id"
    ckan_resource_id_field = "aneel_tarifas_resource_id"

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        starts = [self.parse_datetime(row["cycle_start"]) for row in rows]
        ends = [self.parse_datetime(row["cycle_end"]) for row in rows]
        latest_cycle = max(starts)
        published_at = max(ends)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        observations: list[ParsedObservation] = []
        for row in rows:
            distributor_name = row["distributor"].strip()
            entity_code = distributor_code(distributor_name)
            entity_key = f"distributor:{entity_code}"
            entities_by_key.setdefault(
                entity_key,
                ParsedEntity(
                    key=entity_key,
                    entity_type="distributor",
                    canonical_code=entity_code,
                    name=distributor_name,
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={
                        "source_dataset": self.dataset_code,
                        "source_code": self.source_code,
                        "tax_id": row.get("cnpj", "").strip() or None,
                        "legal_name": distributor_name,
                        "profile_kind": "sector",
                        "role": "distributor",
                        "status": "active",
                    },
                ),
            )
            aliases_by_key.setdefault(
                (entity_key, distributor_name),
                ParsedEntityAlias(
                    entity_key=entity_key,
                    source_code=self.source_code,
                    alias_name=distributor_name,
                    external_code=row.get("cnpj", "").strip() or entity_code,
                    confidence=1.0,
                ),
            )
            observations.append(
                ParsedObservation(
                    series_key="series:tariff_rs_mwh",
                    entity_key=entity_key,
                    time=self.parse_datetime(row["cycle_start"]),
                    value_numeric=float(row["tariff_rs_mwh"]),
                    dimensions={"cycle_end": row["cycle_end"]},
                    published_at=published_at,
                )
            )

        version = ParsedDatasetVersion(
            label=latest_cycle.strftime("%Y-%m"),
            extracted_at=published_at,
            published_at=published_at,
            coverage_start=min(starts),
            coverage_end=max(ends),
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
                    key="series:tariff_rs_mwh",
                    metric_code="tariff_rs_mwh",
                    metric_name="Tarifa",
                    unit="R$/MWh",
                    temporal_granularity="month",
                    entity_type="distributor",
                    semantic_value_type="regulatory_effective",
                    reference_time_kind="effective_date",
                    dimensions={"source": "aneel"},
                )
            ],
            observations=observations,
        )


class AneelSigaAdapter(CkanDatasetAdapter):
    dataset_code = "siga_geracao_aneel"
    source_code = "aneel"
    fixture_name = "aneel_siga_geracao.csv"
    settings_url_field = "aneel_siga_url"
    ckan_base_url_field = "aneel_ckan_base_url"
    ckan_package_id_field = "aneel_siga_package_id"
    ckan_resource_id_field = "aneel_siga_resource_id"

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        published_at = max(self.parse_datetime(row["reference_at"]) for row in rows)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        relations: dict[tuple[str, str, str], ParsedRelation] = {}
        observations: list[ParsedObservation] = []

        for row in rows:
            observed_at = self.parse_datetime(row["reference_at"])
            municipality_id = municipality_code(row["municipality"], row.get("ibge_code"))
            municipality_key = f"municipality:{municipality_id}"
            submarket_code, submarket_name = canonical_submarket(row["submarket"])
            submarket_key = f"submarket:{submarket_code}"
            subsystem_name = row.get("subsystem", submarket_name)
            subsystem_code = row.get("subsystem_code", submarket_code)
            subsystem_key = f"subsystem:{subsystem_code}"
            plant_id = plant_code(row["plant_name"], ceg=row.get("ceg"), ons_plant_code=row.get("ons_plant_code"))
            plant_key = f"plant:{plant_id}"
            agent_id = agent_code(row["agent_name"], row.get("agent_cnpj"))
            agent_key = f"agent:{agent_id}"

            entities_by_key.setdefault(
                municipality_key,
                ParsedEntity(
                    key=municipality_key,
                    entity_type="municipality",
                    canonical_code=municipality_id,
                    name=row["municipality"].strip(),
                    jurisdiction=row["state"].strip(),
                    attributes={
                        "ibge_code": row.get("ibge_code", "").strip() or None,
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
                    canonical_code=subsystem_code,
                    name=subsystem_name.strip(),
                    jurisdiction="SIN",
                    attributes={"source_code": self.source_code, "operator_code": subsystem_code},
                ),
            )
            entities_by_key.setdefault(
                agent_key,
                ParsedEntity(
                    key=agent_key,
                    entity_type="agent",
                    canonical_code=agent_id,
                    name=row["agent_name"].strip(),
                    jurisdiction=row["state"].strip(),
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
            entities_by_key.setdefault(
                plant_key,
                ParsedEntity(
                    key=plant_key,
                    entity_type="plant",
                    canonical_code=plant_id,
                    name=row["plant_name"].strip(),
                    jurisdiction=row["state"].strip(),
                    attributes={
                        "ceg": row.get("ceg", "").strip() or None,
                        "ons_plant_code": row.get("ons_plant_code", "").strip() or None,
                        "source_type": row.get("source_type", "").strip() or None,
                        "fuel_type": row.get("fuel_type", "").strip() or None,
                        "installed_capacity_mw": float(row["installed_capacity_mw"]),
                        "status": row.get("status", "granted").strip() or "granted",
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
                    external_code=row.get("ceg", "").strip() or plant_id,
                    confidence=1.0,
                ),
            )

            relations[(plant_key, agent_key, "OPERATED_BY")] = ParsedRelation(
                relation_type="OPERATED_BY",
                source_entity_key=plant_key,
                target_entity_key=agent_key,
            )
            relations[(plant_key, municipality_key, "LOCATED_IN")] = ParsedRelation(
                relation_type="LOCATED_IN",
                source_entity_key=plant_key,
                target_entity_key=municipality_key,
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

            observations.append(
                ParsedObservation(
                    series_key="series:installed_capacity_mw",
                    entity_key=plant_key,
                    time=observed_at,
                    value_numeric=float(row["installed_capacity_mw"]),
                    published_at=published_at,
                )
            )

        version = ParsedDatasetVersion(
            label=published_at.date().isoformat(),
            extracted_at=published_at,
            published_at=published_at,
            coverage_start=published_at,
            coverage_end=published_at,
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
                    key="series:installed_capacity_mw",
                    metric_code="installed_capacity_mw",
                    metric_name="Capacidade instalada",
                    unit="MW",
                    temporal_granularity="event",
                    entity_type="plant",
                    semantic_value_type="regulatory_effective",
                    reference_time_kind="effective_date",
                    dimensions={"source": "aneel"},
                )
            ],
            observations=observations,
        )


class AneelDecFecAdapter(CkanDatasetAdapter):
    dataset_code = "indicadores_dec_fec"
    source_code = "aneel"
    fixture_name = "aneel_dec_fec.csv"
    settings_url_field = "aneel_dec_fec_url"
    ckan_base_url_field = "aneel_ckan_base_url"
    ckan_package_id_field = "aneel_dec_fec_package_id"
    ckan_resource_id_field = "aneel_dec_fec_resource_id"

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        timestamps = [self.parse_datetime(row["reference_month"]) for row in rows]
        published_at = max(timestamps)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        relations: dict[tuple[str, str, str], ParsedRelation] = {}
        observations: list[ParsedObservation] = []

        for row in rows:
            distributor_name = row["distributor"].strip()
            distributor_id = distributor_code(distributor_name)
            distributor_key = f"distributor:{distributor_id}"
            municipality_id = municipality_code(row["municipality"], row.get("ibge_code"))
            municipality_key = f"municipality:{municipality_id}"
            submarket_code, submarket_name = canonical_submarket(row["submarket"])
            submarket_key = f"submarket:{submarket_code}"
            observed_at = self.parse_datetime(row["reference_month"])

            entities_by_key.setdefault(
                distributor_key,
                ParsedEntity(
                    key=distributor_key,
                    entity_type="distributor",
                    canonical_code=distributor_id,
                    name=distributor_name,
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={
                        "tax_id": row.get("cnpj", "").strip() or None,
                        "legal_name": distributor_name,
                        "profile_kind": "sector",
                        "role": "distributor",
                        "source_code": self.source_code,
                        "status": "active",
                        "municipality_entity_key": municipality_key,
                        "submarket_entity_key": submarket_key,
                    },
                ),
            )
            aliases_by_key.setdefault(
                (distributor_key, distributor_name),
                ParsedEntityAlias(
                    entity_key=distributor_key,
                    source_code=self.source_code,
                    alias_name=distributor_name,
                    external_code=row.get("cnpj", "").strip() or distributor_id,
                    confidence=1.0,
                ),
            )
            entities_by_key.setdefault(
                municipality_key,
                ParsedEntity(
                    key=municipality_key,
                    entity_type="municipality",
                    canonical_code=municipality_id,
                    name=row["municipality"].strip(),
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={"ibge_code": row.get("ibge_code", "").strip() or None, "source_code": self.source_code},
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

            relations[(distributor_key, municipality_key, "HAS_QUALITY_INDICATOR")] = ParsedRelation(
                relation_type="HAS_QUALITY_INDICATOR",
                source_entity_key=distributor_key,
                target_entity_key=municipality_key,
            )
            relations[(distributor_key, submarket_key, "MAPPED_TO_SUBMARKET")] = ParsedRelation(
                relation_type="MAPPED_TO_SUBMARKET",
                source_entity_key=distributor_key,
                target_entity_key=submarket_key,
            )

            observations.append(
                ParsedObservation(
                    series_key="series:dec_hours",
                    entity_key=distributor_key,
                    time=observed_at,
                    value_numeric=float(row["dec_hours"]),
                    dimensions={"municipality_code": municipality_id},
                    published_at=published_at,
                )
            )
            observations.append(
                ParsedObservation(
                    series_key="series:fec_index",
                    entity_key=distributor_key,
                    time=observed_at,
                    value_numeric=float(row["fec_index"]),
                    dimensions={"municipality_code": municipality_id},
                    published_at=published_at,
                )
            )

        version = ParsedDatasetVersion(
            label=published_at.strftime("%Y-%m"),
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
                    key="series:dec_hours",
                    metric_code="dec_hours",
                    metric_name="DEC",
                    unit="h",
                    temporal_granularity="month",
                    entity_type="distributor",
                    semantic_value_type="observed",
                    reference_time_kind="reference_month",
                    dimensions={"source": "aneel"},
                ),
                ParsedMetricSeries(
                    key="series:fec_index",
                    metric_code="fec_index",
                    metric_name="FEC",
                    unit="indice",
                    temporal_granularity="month",
                    entity_type="distributor",
                    semantic_value_type="observed",
                    reference_time_kind="reference_month",
                    dimensions={"source": "aneel"},
                ),
            ],
            observations=observations,
        )

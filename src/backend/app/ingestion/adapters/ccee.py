from __future__ import annotations

from app.ingestion.adapters.common import agent_code, canonical_submarket, normalize_token, plant_code
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


class CceePldAdapter(CkanDatasetAdapter):
    dataset_code = "pld_horario_submercado"
    source_code = "ccee"
    fixture_name = "ccee_pld_horario_submercado.csv"
    settings_url_field = "ccee_pld_url"
    ckan_base_url_field = "ccee_ckan_base_url"
    ckan_package_id_field = "ccee_pld_package_id"
    ckan_resource_id_field = "ccee_pld_resource_id"
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
                    attributes={"source_dataset": self.dataset_code, "source_code": self.source_code, "operator_code": submarket_code},
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
                    series_key="series:pld_rs_mwh",
                    entity_key=entity_key,
                    time=entity_timestamp,
                    value_numeric=float(row["pld_rs_mwh"]),
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
                    key="series:pld_rs_mwh",
                    metric_code="pld_rs_mwh",
                    metric_name="PLD",
                    unit="R$/MWh",
                    temporal_granularity="hour",
                    entity_type="submarket",
                    semantic_value_type="accounted",
                    reference_time_kind="instant",
                    dimensions={"source": "ccee"},
                )
            ],
            observations=observations,
        )


class CceePldMediaDiariaAdapter(CkanDatasetAdapter):
    dataset_code = "pld_media_diaria"
    source_code = "ccee"
    fixture_name = "ccee_pld_media_diaria.csv"
    settings_url_field = "ccee_pld_media_diaria_url"
    ckan_base_url_field = "ccee_ckan_base_url"
    ckan_package_id_field = "ccee_pld_media_diaria_package_id"
    ckan_resource_id_field = "ccee_pld_media_diaria_resource_id"
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
                    series_key="series:pld_avg_rs_mwh",
                    entity_key=entity_key,
                    time=entity_timestamp,
                    value_numeric=float(row["pld_avg_rs_mwh"]),
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
                    key="series:pld_avg_rs_mwh",
                    metric_code="pld_avg_rs_mwh",
                    metric_name="PLD medio diario",
                    unit="R$/MWh",
                    temporal_granularity="day",
                    entity_type="submarket",
                    semantic_value_type="accounted",
                    reference_time_kind="instant",
                    dimensions={"source": "ccee"},
                )
            ],
            observations=observations,
        )


class CceeAgentesAdapter(CkanDatasetAdapter):
    dataset_code = "agentes_mercado_ccee"
    source_code = "ccee"
    fixture_name = "ccee_agentes_mercado.csv"
    settings_url_field = "ccee_agentes_url"
    ckan_base_url_field = "ccee_ckan_base_url"
    ckan_package_id_field = "ccee_agentes_package_id"
    ckan_resource_id_field = "ccee_agentes_resource_id"
    prefer_datastore = True

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        rows = self.parse_csv_rows(raw_bytes)
        timestamps = [self.parse_datetime(row["reference_month"]) for row in rows]
        published_at = max(timestamps)

        entities_by_key: dict[str, ParsedEntity] = {}
        aliases_by_key: dict[tuple[str, str], ParsedEntityAlias] = {}
        for row in rows:
            entity_code = agent_code(row["legal_name"], row.get("tax_id"))
            entity_key = f"agent:{entity_code}"
            entities_by_key.setdefault(
                entity_key,
                ParsedEntity(
                    key=entity_key,
                    entity_type="agent",
                    canonical_code=entity_code,
                    name=row["legal_name"].strip(),
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={
                        "tax_id": row.get("tax_id", "").strip() or None,
                        "legal_name": row["legal_name"].strip(),
                        "trade_name": row.get("agent_code", "").strip() or None,
                        "profile_kind": "market",
                        "role": row.get("agent_class", "market_agent").strip().lower(),
                        "source_code": self.source_code,
                        "status": row.get("status", "active").strip() or "active",
                    },
                ),
            )
            aliases_by_key.setdefault(
                (entity_key, row["legal_name"]),
                ParsedEntityAlias(
                    entity_key=entity_key,
                    source_code=self.source_code,
                    alias_name=row["legal_name"].strip(),
                    external_code=row.get("tax_id", "").strip() or entity_code,
                    confidence=1.0,
                ),
            )
            if row.get("agent_code"):
                aliases_by_key.setdefault(
                    (entity_key, row["agent_code"]),
                    ParsedEntityAlias(
                        entity_key=entity_key,
                        source_code=self.source_code,
                        alias_name=row["agent_code"].strip(),
                        external_code=row["agent_code"].strip(),
                        confidence=1.0,
                    ),
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
        )


class CceeInfomercadoGeracaoAdapter(CkanDatasetAdapter):
    dataset_code = "infomercado_geracao_horaria_usina"
    source_code = "ccee"
    fixture_name = "ccee_infomercado_geracao_horaria_usina.csv"
    settings_url_field = "ccee_infomercado_geracao_url"
    ckan_base_url_field = "ccee_ckan_base_url"
    ckan_package_id_field = "ccee_infomercado_geracao_package_id"
    ckan_resource_id_field = "ccee_infomercado_geracao_resource_id"
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
            agent_id = agent_code(row["agent_name"], row.get("agent_tax_id"))
            agent_key = f"agent:{agent_id}"
            plant_id = plant_code(row["plant_name"], ceg=row.get("ceg"), ons_plant_code=row.get("ons_plant_code"))
            plant_key = f"plant:{plant_id}"
            submarket_code, submarket_name = canonical_submarket(row["submarket"])
            submarket_key = f"submarket:{submarket_code}"

            entities_by_key.setdefault(
                agent_key,
                ParsedEntity(
                    key=agent_key,
                    entity_type="agent",
                    canonical_code=agent_id,
                    name=row["agent_name"].strip(),
                    jurisdiction=row.get("state", "BR") or "BR",
                    attributes={
                        "tax_id": row.get("agent_tax_id", "").strip() or None,
                        "legal_name": row["agent_name"].strip(),
                        "trade_name": row.get("agent_code", "").strip() or None,
                        "profile_kind": "market",
                        "role": "seller",
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
                    external_code=row.get("agent_tax_id", "").strip() or agent_id,
                    confidence=1.0,
                ),
            )
            if row.get("agent_code"):
                aliases_by_key.setdefault(
                    (agent_key, row["agent_code"]),
                    ParsedEntityAlias(
                        entity_key=agent_key,
                        source_code=self.source_code,
                        alias_name=row["agent_code"].strip(),
                        external_code=row["agent_code"].strip(),
                        confidence=1.0,
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
                        "submarket_entity_key": submarket_key,
                        "source_code": self.source_code,
                        "status": "accounted",
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
            relations[(plant_key, submarket_key, "MAPPED_TO_SUBMARKET")] = ParsedRelation(
                relation_type="MAPPED_TO_SUBMARKET",
                source_entity_key=plant_key,
                target_entity_key=submarket_key,
            )

            observations.append(
                ParsedObservation(
                    series_key="series:accounted_generation_mwh",
                    entity_key=plant_key,
                    time=observation_time,
                    value_numeric=float(row["generation_mwh"]),
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
                    key="series:accounted_generation_mwh",
                    metric_code="accounted_generation_mwh",
                    metric_name="Geracao contabilizada",
                    unit="MWh",
                    temporal_granularity="hour",
                    entity_type="plant",
                    semantic_value_type="accounted",
                    reference_time_kind="instant",
                    dimensions={"source": "ccee"},
                )
            ],
            observations=observations,
        )

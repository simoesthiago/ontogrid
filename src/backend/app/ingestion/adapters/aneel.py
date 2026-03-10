from __future__ import annotations

from app.ingestion.adapters.common import distributor_code
from app.ingestion.base import (
    CkanDatasetAdapter,
    ParsedDatasetPayload,
    ParsedDatasetVersion,
    ParsedEntity,
    ParsedEntityAlias,
    ParsedMetricSeries,
    ParsedObservation,
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
                    jurisdiction="BR",
                    attributes={"source_dataset": self.dataset_code},
                ),
            )
            aliases_by_key.setdefault(
                (entity_key, distributor_name),
                ParsedEntityAlias(
                    entity_key=entity_key,
                    source_code=self.source_code,
                    alias_name=distributor_name,
                    external_code=entity_code,
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
                    dimensions={"source": "aneel"},
                )
            ],
            observations=observations,
        )

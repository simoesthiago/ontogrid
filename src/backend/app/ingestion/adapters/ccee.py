from __future__ import annotations

from app.ingestion.adapters.common import canonical_submarket, normalize_token
from app.ingestion.base import (
    CkanDatasetAdapter,
    ParsedDatasetPayload,
    ParsedDatasetVersion,
    ParsedEntity,
    ParsedEntityAlias,
    ParsedMetricSeries,
    ParsedObservation,
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
                    attributes={"source_dataset": self.dataset_code},
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
                    dimensions={"source": "ccee"},
                )
            ],
            observations=observations,
        )

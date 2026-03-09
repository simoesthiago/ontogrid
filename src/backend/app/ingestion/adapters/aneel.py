from __future__ import annotations

from app.ingestion.base import BaseDatasetAdapter, ParsedDatasetVersion


class AneelTarifasAdapter(BaseDatasetAdapter):
    dataset_code = "tarifas_distribuicao"
    source_code = "aneel"
    fixture_name = "aneel_tarifas_distribuicao.csv"
    settings_url_field = "aneel_tarifas_url"

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetVersion:
        rows = self.parse_csv_rows(raw_bytes)
        starts = [self.parse_datetime(row["cycle_start"]) for row in rows]
        ends = [self.parse_datetime(row["cycle_end"]) for row in rows]
        latest_cycle = max(starts)
        return ParsedDatasetVersion(
            label=latest_cycle.strftime("%Y-%m"),
            extracted_at=max(ends),
            published_at=max(ends),
            coverage_start=min(starts),
            coverage_end=max(ends),
            row_count=len(rows),
            schema_version="v1",
            checksum=checksum,
        )

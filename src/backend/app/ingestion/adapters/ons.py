from __future__ import annotations

from app.ingestion.base import BaseDatasetAdapter, ParsedDatasetVersion


class OnsCargaAdapter(BaseDatasetAdapter):
    dataset_code = "carga_horaria_submercado"
    source_code = "ons"
    fixture_name = "ons_carga_horaria_submercado.csv"
    settings_url_field = "ons_carga_url"

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetVersion:
        rows = self.parse_csv_rows(raw_bytes)
        timestamps = [self.parse_datetime(row["timestamp"]) for row in rows]
        return ParsedDatasetVersion(
            label=max(timestamps).date().isoformat(),
            extracted_at=max(timestamps),
            published_at=max(timestamps),
            coverage_start=min(timestamps),
            coverage_end=max(timestamps),
            row_count=len(rows),
            schema_version="v1",
            checksum=checksum,
        )

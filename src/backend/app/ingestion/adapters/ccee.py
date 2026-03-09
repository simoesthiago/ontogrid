from __future__ import annotations

from app.ingestion.base import BaseDatasetAdapter, ParsedDatasetVersion


class CceePldAdapter(BaseDatasetAdapter):
    dataset_code = "pld_horario_submercado"
    source_code = "ccee"
    fixture_name = "ccee_pld_horario_submercado.csv"
    settings_url_field = "ccee_pld_url"

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

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

from app.core.config import Settings


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass
class ParsedDatasetVersion:
    label: str
    extracted_at: datetime
    published_at: datetime
    coverage_start: datetime | None
    coverage_end: datetime | None
    row_count: int
    schema_version: str
    checksum: str


class BaseDatasetAdapter:
    dataset_code: str
    source_code: str
    fixture_name: str
    settings_url_field: str
    file_extension: str = ".csv"

    def bootstrap_bytes(self) -> bytes:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / self.fixture_name
        return fixture_path.read_bytes()

    def fetch_bytes(self, settings: Settings) -> bytes:
        source_url = getattr(settings, self.settings_url_field)
        if not source_url:
            raise ValueError(f"Missing source URL configuration for dataset {self.dataset_code}")
        with urlopen(source_url) as response:
            return response.read()

    def checksum(self, raw_bytes: bytes) -> str:
        return hashlib.sha256(raw_bytes).hexdigest()

    def parse_csv_rows(self, raw_bytes: bytes) -> list[dict[str, str]]:
        text = raw_bytes.decode("utf-8-sig")
        reader = csv.DictReader(StringIO(text))
        rows = list(reader)
        if not rows:
            raise ValueError(f"Dataset {self.dataset_code} returned an empty artifact")
        return rows

    def parse_datetime(self, value: str) -> datetime:
        normalized = value.strip().replace("Z", "+00:00")
        return ensure_utc(datetime.fromisoformat(normalized))

    def artifact_metadata(self, artifact_path: Path, raw_bytes: bytes) -> dict[str, str]:
        return {
            "artifact_path": str(artifact_path),
            "artifact_size_bytes": str(len(raw_bytes)),
            "artifact_format": self.file_extension.lstrip("."),
        }

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetVersion:
        raise NotImplementedError

    def dump_preview(self, raw_bytes: bytes) -> str:
        try:
            rows = self.parse_csv_rows(raw_bytes)
        except Exception:
            return json.dumps({"preview": "unavailable"})
        return json.dumps(rows[:3], ensure_ascii=True)

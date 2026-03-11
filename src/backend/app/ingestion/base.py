from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.parse import urlencode
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


@dataclass
class ParsedEntity:
    key: str
    entity_type: str
    name: str
    canonical_code: str | None = None
    jurisdiction: str = "BR"
    attributes: dict[str, object] = field(default_factory=dict)


@dataclass
class ParsedEntityAlias:
    entity_key: str
    source_code: str
    alias_name: str
    external_code: str | None = None
    confidence: float | None = None


@dataclass
class ParsedRelation:
    relation_type: str
    source_entity_key: str
    target_entity_key: str
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    attributes: dict[str, object] = field(default_factory=dict)


@dataclass
class ParsedMetricSeries:
    key: str
    metric_code: str
    metric_name: str
    unit: str
    temporal_granularity: str
    entity_type: str
    semantic_value_type: str = "observed"
    reference_time_kind: str = "instant"
    dimensions: dict[str, object] = field(default_factory=dict)


@dataclass
class ParsedObservation:
    series_key: str
    entity_key: str
    time: datetime
    value_numeric: float | None = None
    value_text: str | None = None
    quality_flag: str = "published"
    dimensions: dict[str, object] = field(default_factory=dict)
    published_at: datetime | None = None


@dataclass
class ParsedDatasetPayload:
    dataset_version: ParsedDatasetVersion
    entities: list[ParsedEntity] = field(default_factory=list)
    aliases: list[ParsedEntityAlias] = field(default_factory=list)
    relations: list[ParsedRelation] = field(default_factory=list)
    metric_series: list[ParsedMetricSeries] = field(default_factory=list)
    observations: list[ParsedObservation] = field(default_factory=list)


class BaseDatasetAdapter:
    dataset_code: str
    source_code: str
    fixture_name: str
    settings_url_field: str
    file_extension: str = ".csv"

    def __init__(self) -> None:
        self._last_fetch_metadata: dict[str, str] = {}

    def bootstrap_bytes(self) -> bytes:
        self._last_fetch_metadata = {"fetch_mode": "fixture"}
        fixture_path = Path(__file__).resolve().parent / "fixtures" / self.fixture_name
        return fixture_path.read_bytes()

    def fetch_bytes(self, settings: Settings) -> bytes:
        source_url = getattr(settings, self.settings_url_field)
        if not source_url:
            raise ValueError(f"Missing source URL configuration for dataset {self.dataset_code}")
        self._last_fetch_metadata = {"fetch_mode": "direct_url", "source_url": source_url}
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
            **self._last_fetch_metadata,
        }

    def parse(self, raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
        raise NotImplementedError

    def dump_preview(self, raw_bytes: bytes) -> str:
        try:
            rows = self.parse_csv_rows(raw_bytes)
        except Exception:
            return json.dumps({"preview": "unavailable"})
        return json.dumps(rows[:3], ensure_ascii=True)


class CkanDatasetAdapter(BaseDatasetAdapter):
    ckan_base_url_field: str
    ckan_package_id_field: str
    ckan_resource_id_field: str
    prefer_datastore: bool = False
    preferred_formats: tuple[str, ...] = ("csv",)
    preferred_name_tokens: tuple[str, ...] = ()

    def fetch_bytes(self, settings: Settings) -> bytes:
        direct_url = getattr(settings, self.settings_url_field, "")
        if direct_url:
            return super().fetch_bytes(settings)

        base_url = getattr(settings, self.ckan_base_url_field)
        package_id = getattr(settings, self.ckan_package_id_field)
        resource_id = getattr(settings, self.ckan_resource_id_field)
        if not base_url or not package_id:
            raise ValueError(
                f"Missing CKAN configuration for dataset {self.dataset_code}: "
                f"{self.ckan_base_url_field} and {self.ckan_package_id_field} are required"
            )

        resource = self._resolve_resource(base_url, package_id, resource_id or None)
        resource_url = resource.get("url")
        if not resource_url:
            raise ValueError(f"CKAN resource for dataset {self.dataset_code} does not expose a download URL")

        self._last_fetch_metadata = {
            "fetch_mode": "ckan",
            "ckan_base_url": base_url,
            "ckan_package_id": package_id,
            "ckan_resource_id": str(resource.get("id", "")),
            "source_url": str(resource_url),
        }

        if self.prefer_datastore and resource.get("datastore_active"):
            return self.fetch_via_datastore(base_url, str(resource["id"]))

        with urlopen(str(resource_url)) as response:
            return response.read()

    def fetch_via_datastore(self, base_url: str, resource_id: str, batch_size: int = 10000) -> bytes:
        rows: list[dict[str, object]] = []
        offset = 0
        while True:
            result = self._call_ckan_action(
                base_url,
                "datastore_search",
                {"resource_id": resource_id, "limit": str(batch_size), "offset": str(offset)},
            )
            records = result.get("records", [])
            if not records:
                break
            rows.extend(records)
            if len(records) < batch_size:
                break
            offset += batch_size

        if not rows:
            raise ValueError(f"CKAN datastore for dataset {self.dataset_code} returned no rows")

        fieldnames = list(rows[0].keys())
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8")

    def _resolve_resource(self, base_url: str, package_id: str, resource_id: str | None) -> dict[str, object]:
        if resource_id:
            result = self._call_ckan_action(base_url, "resource_show", {"id": resource_id})
            return result

        package = self._call_ckan_action(base_url, "package_show", {"id": package_id})
        resources = package.get("resources", [])
        if not resources:
            raise ValueError(f"CKAN package {package_id} for dataset {self.dataset_code} has no resources")

        candidates = [resource for resource in resources if self._resource_matches(resource)]
        if not candidates:
            candidates = list(resources)
        candidates.sort(key=self._resource_sort_key, reverse=True)
        return candidates[0]

    def _resource_matches(self, resource: dict[str, object]) -> bool:
        resource_format = str(resource.get("format", "")).lower()
        if self.preferred_formats and resource_format not in self.preferred_formats:
            return False
        if not self.preferred_name_tokens:
            return True
        name_blob = " ".join(
            str(resource.get(field, "")).lower()
            for field in ("name", "description", "url")
        )
        return all(token.lower() in name_blob for token in self.preferred_name_tokens)

    def _resource_sort_key(self, resource: dict[str, object]) -> tuple[int, str, str]:
        text = " ".join(str(resource.get(field, "")) for field in ("name", "description", "url"))
        years = [int(match) for match in re.findall(r"(?:19|20)\d{2}", text)]
        best_year = max(years) if years else 0
        freshness = str(resource.get("last_modified") or resource.get("created") or "")
        return (best_year, freshness, str(resource.get("id", "")))

    def _call_ckan_action(self, base_url: str, action: str, params: dict[str, str]) -> dict[str, object]:
        action_url = f"{base_url.rstrip('/')}/api/3/action/{action}?{urlencode(params)}"
        with urlopen(action_url) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("success"):
            raise ValueError(f"CKAN action {action} failed for dataset {self.dataset_code}")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError(f"CKAN action {action} returned an unexpected payload for dataset {self.dataset_code}")
        return result

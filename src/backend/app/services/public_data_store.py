from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class PublicDataStore:
    def __init__(self) -> None:
        self.sources = [
            {
                "id": "src-aneel",
                "code": "aneel",
                "name": "ANEEL",
                "authority_type": "regulator",
                "refresh_strategy": "scheduled_download",
                "status": "active",
            },
            {
                "id": "src-ons",
                "code": "ons",
                "name": "ONS",
                "authority_type": "system_operator",
                "refresh_strategy": "scheduled_download",
                "status": "active",
            },
            {
                "id": "src-ccee",
                "code": "ccee",
                "name": "CCEE",
                "authority_type": "market_operator",
                "refresh_strategy": "scheduled_download",
                "status": "active",
            },
        ]
        self.datasets = [
            {
                "id": "ds-ons-carga",
                "source_id": "src-ons",
                "source_code": "ons",
                "code": "carga_horaria_submercado",
                "name": "Carga horaria por submercado",
                "domain": "operacao",
                "description": "Serie horaria curada a partir do portal publico do ONS.",
                "granularity": "hour",
                "refresh_frequency": "daily",
                "schema_summary": {"dimensions": ["submarket"], "metrics": ["load_mw"]},
                "latest_version": {
                    "id": "ver-ons-carga-2026-03-09",
                    "label": "2026-03-09",
                    "published_at": "2026-03-09T12:00:00Z",
                },
                "latest_published_at": "2026-03-09T12:00:00Z",
                "freshness_status": "fresh",
            },
            {
                "id": "ds-aneel-tarifas",
                "source_id": "src-aneel",
                "source_code": "aneel",
                "code": "tarifas_distribuicao",
                "name": "Tarifas homologadas de distribuicao",
                "domain": "regulatorio",
                "description": "Base publica harmonizada de tarifas e ciclos homologatorios.",
                "granularity": "month",
                "refresh_frequency": "monthly",
                "schema_summary": {"dimensions": ["distributor"], "metrics": ["tariff_rs_mwh"]},
                "latest_version": {
                    "id": "ver-aneel-tarifas-2026-03",
                    "label": "2026-03",
                    "published_at": "2026-03-08T09:00:00Z",
                },
                "latest_published_at": "2026-03-08T09:00:00Z",
                "freshness_status": "fresh",
            },
            {
                "id": "ds-ccee-pld",
                "source_id": "src-ccee",
                "source_code": "ccee",
                "code": "pld_horario_submercado",
                "name": "PLD horario por submercado",
                "domain": "mercado",
                "description": "Serie publica do preco de liquidacao das diferencas por submercado.",
                "granularity": "hour",
                "refresh_frequency": "daily",
                "schema_summary": {"dimensions": ["submarket"], "metrics": ["pld_rs_mwh"]},
                "latest_version": {
                    "id": "ver-ccee-pld-2026-03-09",
                    "label": "2026-03-09",
                    "published_at": "2026-03-09T10:30:00Z",
                },
                "latest_published_at": "2026-03-09T10:30:00Z",
                "freshness_status": "fresh",
            },
        ]
        self.dataset_versions = {
            "ds-ons-carga": [
                {
                    "id": "ver-ons-carga-2026-03-09",
                    "dataset_id": "ds-ons-carga",
                    "label": "2026-03-09",
                    "extracted_at": "2026-03-09T11:55:00Z",
                    "published_at": "2026-03-09T12:00:00Z",
                    "coverage_start": "2026-03-01T00:00:00Z",
                    "coverage_end": "2026-03-09T23:00:00Z",
                    "status": "published",
                    "checksum": "sha256-ons-carga",
                    "row_count": 744,
                    "schema_version": "v1",
                    "lineage": {"source_code": "ons", "refresh_job_id": "job-ons-carga-20260309"},
                }
            ],
            "ds-aneel-tarifas": [
                {
                    "id": "ver-aneel-tarifas-2026-03",
                    "dataset_id": "ds-aneel-tarifas",
                    "label": "2026-03",
                    "extracted_at": "2026-03-08T08:40:00Z",
                    "published_at": "2026-03-08T09:00:00Z",
                    "coverage_start": "2026-03-01T00:00:00Z",
                    "coverage_end": "2026-03-31T23:59:59Z",
                    "status": "published",
                    "checksum": "sha256-aneel-tarifas",
                    "row_count": 124,
                    "schema_version": "v1",
                    "lineage": {"source_code": "aneel", "refresh_job_id": "job-aneel-tarifas-20260308"},
                }
            ],
            "ds-ccee-pld": [
                {
                    "id": "ver-ccee-pld-2026-03-09",
                    "dataset_id": "ds-ccee-pld",
                    "label": "2026-03-09",
                    "extracted_at": "2026-03-09T10:00:00Z",
                    "published_at": "2026-03-09T10:30:00Z",
                    "coverage_start": "2026-03-09T00:00:00Z",
                    "coverage_end": "2026-03-09T23:00:00Z",
                    "status": "published",
                    "checksum": "sha256-ccee-pld",
                    "row_count": 96,
                    "schema_version": "v1",
                    "lineage": {"source_code": "ccee", "refresh_job_id": "job-ccee-pld-20260309"},
                }
            ],
        }
        self.series = [
            {
                "id": "ser-load-mw",
                "dataset_id": "ds-ons-carga",
                "metric_code": "load_mw",
                "metric_name": "Carga",
                "unit": "MW",
                "temporal_granularity": "hour",
                "entity_type": "submarket",
                "latest_observation_at": "2026-03-09T23:00:00Z",
            },
            {
                "id": "ser-tariff-rs-mwh",
                "dataset_id": "ds-aneel-tarifas",
                "metric_code": "tariff_rs_mwh",
                "metric_name": "Tarifa",
                "unit": "R$/MWh",
                "temporal_granularity": "month",
                "entity_type": "distributor",
                "latest_observation_at": "2026-03-01T00:00:00Z",
            },
            {
                "id": "ser-pld-rs-mwh",
                "dataset_id": "ds-ccee-pld",
                "metric_code": "pld_rs_mwh",
                "metric_name": "PLD",
                "unit": "R$/MWh",
                "temporal_granularity": "hour",
                "entity_type": "submarket",
                "latest_observation_at": "2026-03-09T23:00:00Z",
            },
        ]
        self.observations = {
            "ser-load-mw": {
                "dataset_version_id": "ver-ons-carga-2026-03-09",
                "items": [
                    {
                        "timestamp": "2026-03-09T21:00:00Z",
                        "value": 81102.4,
                        "unit": "MW",
                        "quality_flag": "published",
                        "published_at": "2026-03-09T12:00:00Z",
                    },
                    {
                        "timestamp": "2026-03-09T22:00:00Z",
                        "value": 82418.9,
                        "unit": "MW",
                        "quality_flag": "published",
                        "published_at": "2026-03-09T12:00:00Z",
                    },
                    {
                        "timestamp": "2026-03-09T23:00:00Z",
                        "value": 80577.1,
                        "unit": "MW",
                        "quality_flag": "published",
                        "published_at": "2026-03-09T12:00:00Z",
                    },
                ],
            },
            "ser-tariff-rs-mwh": {
                "dataset_version_id": "ver-aneel-tarifas-2026-03",
                "items": [
                    {
                        "timestamp": "2026-03-01T00:00:00Z",
                        "value": 412.7,
                        "unit": "R$/MWh",
                        "quality_flag": "published",
                        "published_at": "2026-03-08T09:00:00Z",
                    }
                ],
            },
            "ser-pld-rs-mwh": {
                "dataset_version_id": "ver-ccee-pld-2026-03-09",
                "items": [
                    {
                        "timestamp": "2026-03-09T21:00:00Z",
                        "value": 186.4,
                        "unit": "R$/MWh",
                        "quality_flag": "published",
                        "published_at": "2026-03-09T10:30:00Z",
                    },
                    {
                        "timestamp": "2026-03-09T22:00:00Z",
                        "value": 179.2,
                        "unit": "R$/MWh",
                        "quality_flag": "published",
                        "published_at": "2026-03-09T10:30:00Z",
                    },
                ],
            },
        }
        self.entities = [
            {
                "id": "ent-se-co",
                "entity_type": "submarket",
                "name": "Sudeste/Centro-Oeste",
                "source": "ons",
                "alias_count": 2,
            },
            {
                "id": "ent-nordeste",
                "entity_type": "submarket",
                "name": "Nordeste",
                "source": "ons",
                "alias_count": 1,
            },
            {
                "id": "ent-enel-sp",
                "entity_type": "distributor",
                "name": "Enel SP",
                "source": "aneel",
                "alias_count": 3,
            },
        ]
        self.neighbors = {
            "ent-se-co": {
                "entity_id": "ent-se-co",
                "nodes": [
                    {"id": "ent-se-co", "type": "Submarket", "name": "Sudeste/Centro-Oeste"},
                    {"id": "ds-ons-carga", "type": "Dataset", "name": "Carga horaria por submercado"},
                    {"id": "ds-ccee-pld", "type": "Dataset", "name": "PLD horario por submercado"},
                ],
                "edges": [
                    {"source": "ds-ons-carga", "target": "ent-se-co", "type": "MEASURES"},
                    {"source": "ds-ccee-pld", "target": "ent-se-co", "type": "PRICES"},
                ],
            }
        }

    def list_sources(self, q: str | None, status: str | None) -> list[dict]:
        items = self.sources
        if q:
            term = q.lower()
            items = [item for item in items if term in item["name"].lower() or term in item["code"].lower()]
        if status:
            items = [item for item in items if item["status"] == status]
        return items

    def list_datasets(self, source: str | None, domain: str | None, granularity: str | None, q: str | None) -> list[dict]:
        items = self.datasets
        if source:
            items = [item for item in items if item["source_code"] == source]
        if domain:
            items = [item for item in items if item["domain"] == domain]
        if granularity:
            items = [item for item in items if item["granularity"] == granularity]
        if q:
            term = q.lower()
            items = [item for item in items if term in item["name"].lower() or term in item["code"].lower()]
        return items

    def get_dataset(self, dataset_id: str) -> dict | None:
        return next((item for item in self.datasets if item["id"] == dataset_id), None)

    def list_dataset_versions(self, dataset_id: str) -> list[dict]:
        return self.dataset_versions.get(dataset_id, [])

    def get_dataset_version(self, dataset_id: str, version_id: str) -> dict | None:
        versions = self.dataset_versions.get(dataset_id, [])
        return next((item for item in versions if item["id"] == version_id), None)

    def create_refresh_job(self, dataset_id: str) -> dict:
        return {
            "refresh_job_id": str(uuid4()),
            "dataset_id": dataset_id,
            "status": "queued",
            "requested_at": utc_timestamp(),
        }

    def list_series(self, dataset_id: str | None, entity_id: str | None, metric_code: str | None, q: str | None) -> list[dict]:
        items = self.series
        if dataset_id:
            items = [item for item in items if item["dataset_id"] == dataset_id]
        if entity_id:
            entity = next((item for item in self.entities if item["id"] == entity_id), None)
            if entity is not None:
                items = [item for item in items if item["entity_type"] == entity["entity_type"]]
            else:
                items = []
        if metric_code:
            items = [item for item in items if item["metric_code"] == metric_code]
        if q:
            term = q.lower()
            items = [item for item in items if term in item["metric_name"].lower() or term in item["metric_code"].lower()]
        return items

    def get_observations(self, series_id: str) -> dict | None:
        return self.observations.get(series_id)

    def list_entities(self, q: str | None, entity_type: str | None, source: str | None) -> list[dict]:
        items = self.entities
        if q:
            term = q.lower()
            items = [item for item in items if term in item["name"].lower()]
        if entity_type:
            items = [item for item in items if item["entity_type"] == entity_type]
        if source:
            items = [item for item in items if item["source"] == source]
        return items

    def get_neighbors(self, entity_id: str) -> dict | None:
        return self.neighbors.get(entity_id)


store = PublicDataStore()

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.copilot.cache import get_copilot_cache
from app.copilot.client import get_llm_client
from app.copilot.service import get_copilot_service
from app.core.config import get_settings
from app.db.migrations import upgrade_database
from app.db.models import Dataset, Entity, Observation, Relation
from app.db.session import get_session_factory, reset_db_caches
from app.main import create_app
from app.services.graph_service import get_graph_service


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "app" / "ingestion" / "fixtures"
TEST_RUNTIME_DIR = Path(__file__).resolve().parents[1] / ".tmp" / "test-runtime"


class FakeGraphProjection:
    def __init__(self) -> None:
        self.entities: dict[str, dict[str, object]] = {}
        self.datasets: dict[str, dict[str, object]] = {}
        self.dataset_refs: dict[tuple[str, str], dict[str, str]] = {}
        self.relations: dict[tuple[str, str, str, str], dict[str, str]] = {}

    def project_dataset_version(self, session, dataset_id: str, dataset_version_id: str) -> None:
        dataset = session.scalar(
            select(Dataset)
            .options(joinedload(Dataset.source))
            .where(Dataset.id == dataset_id)
        )
        if dataset is None or dataset.source is None:
            return

        self.datasets[dataset.id] = {
            "id": dataset.id,
            "name": dataset.name,
            "source_code": dataset.source.code,
            "dataset_version_id": dataset_version_id,
        }
        for key in [ref_key for ref_key in self.dataset_refs if ref_key[0] == dataset_id]:
            self.dataset_refs.pop(key, None)
        for key in [edge_key for edge_key in self.relations if edge_key[3] == dataset_id]:
            self.relations.pop(key, None)

        entity_ids = set(
            session.scalars(
                select(Observation.entity_id).where(Observation.dataset_version_id == dataset_version_id)
            ).all()
        )
        relation_rows = session.scalars(
            select(Relation).where(Relation.dataset_version_id == dataset_version_id)
        ).all()
        for relation in relation_rows:
            entity_ids.add(relation.source_entity_id)
            entity_ids.add(relation.target_entity_id)

        if entity_ids:
            entities = session.scalars(
                select(Entity)
                .where(Entity.id.in_(entity_ids))
                .options(selectinload(Entity.aliases))
            ).all()
            for entity in entities:
                self.entities[entity.id] = {
                    "id": entity.id,
                    "entity_type": entity.entity_type,
                    "canonical_code": entity.canonical_code or "",
                    "name": entity.name,
                    "aliases": sorted({alias.alias_name for alias in entity.aliases}),
                    "jurisdiction": entity.jurisdiction,
                    "attributes": dict(entity.attributes),
                }
                self.dataset_refs[(dataset.id, entity.id)] = {
                    "dataset_version_id": dataset_version_id,
                }

        for relation in relation_rows:
            self.relations[
                (
                    relation.source_entity_id,
                    relation.target_entity_id,
                    relation.relation_type,
                    dataset.id,
                )
            ] = {
                "dataset_version_id": relation.dataset_version_id,
            }

    def list_entities(self, session, *, q, entity_type, source, limit, offset):
        del session
        term = q.lower() if q else None
        items = list(self.entities.values())
        if entity_type:
            items = [item for item in items if item["entity_type"] == entity_type]
        if source:
            allowed_ids = {
                entity_id
                for (dataset_id, entity_id), ref in self.dataset_refs.items()
                if ref and self.datasets.get(dataset_id, {}).get("source_code") == source
            }
            items = [item for item in items if item["id"] in allowed_ids]
        if term:
            items = [
                item
                for item in items
                if term in item["name"].lower()
                or term in item["canonical_code"].lower()
                or any(term in alias.lower() for alias in item["aliases"])
            ]
        items.sort(key=lambda item: (str(item["entity_type"]), str(item["name"])))
        total = len(items)
        return items[offset : offset + limit], total

    def get_entity(self, session, entity_id: str):
        del session
        entity = self.entities.get(entity_id)
        if entity is None:
            return None
        return {
            "id": entity["id"],
            "entity_type": entity["entity_type"],
            "canonical_code": entity["canonical_code"],
            "name": entity["name"],
            "attributes": entity["attributes"],
        }

    def get_neighbors(self, session, entity_id: str):
        del session
        entity = self.entities.get(entity_id)
        if entity is None:
            return None

        nodes = {
            entity_id: {"id": entity_id, "type": "Entity", "name": str(entity["name"])},
        }
        edges: dict[tuple[str, str, str], dict[str, str]] = {}
        provenance_ids: set[str] = set()

        for (dataset_id, ref_entity_id), ref in self.dataset_refs.items():
            if ref_entity_id != entity_id:
                continue
            dataset = self.datasets[dataset_id]
            nodes[dataset_id] = {"id": dataset_id, "type": "Dataset", "name": str(dataset["name"])}
            edges[(dataset_id, entity_id, "REFERENCES")] = {
                "source": dataset_id,
                "target": entity_id,
                "type": "REFERENCES",
            }
            provenance_ids.add(ref["dataset_version_id"])

        for (source_id, target_id, relation_type, _dataset_id), relation in self.relations.items():
            if entity_id not in {source_id, target_id}:
                continue
            source_entity = self.entities[source_id]
            target_entity = self.entities[target_id]
            nodes[source_id] = {"id": source_id, "type": "Entity", "name": str(source_entity["name"])}
            nodes[target_id] = {"id": target_id, "type": "Entity", "name": str(target_entity["name"])}
            edges[(source_id, target_id, relation_type)] = {
                "source": source_id,
                "target": target_id,
                "type": relation_type,
            }
            provenance_ids.add(relation["dataset_version_id"])

        return {
            "entity_id": entity_id,
            "nodes": list(nodes.values()),
            "edges": list(edges.values()),
            "provenance": {"dataset_version_ids": sorted(provenance_ids)},
        }


def reset_runtime_state() -> None:
    get_settings.cache_clear()
    reset_db_caches()
    get_graph_service.cache_clear()
    get_copilot_cache.cache_clear()
    get_llm_client.cache_clear()
    get_copilot_service.cache_clear()


def configure_test_environment(
    monkeypatch: pytest.MonkeyPatch,
    runtime_dir: Path,
    *,
    scheduler_enabled: bool = False,
    scheduler_force_run_on_startup: bool = False,
    seed_demo_catalog: bool = True,
    url_overrides: dict[str, str] | None = None,
    env_overrides: dict[str, str] | None = None,
) -> None:
    db_path = runtime_dir / "ontogrid-test.db"
    artifacts_dir = runtime_dir / "artifacts"
    default_urls = {
        "ONS_CARGA_URL": (FIXTURE_DIR / "ons_carga_horaria_submercado.csv").as_uri(),
        "ONS_GERACAO_USINA_URL": (FIXTURE_DIR / "ons_geracao_usina_horaria.csv").as_uri(),
        "ANEEL_TARIFAS_URL": (FIXTURE_DIR / "aneel_tarifas_distribuicao.csv").as_uri(),
        "ANEEL_SIGA_URL": (FIXTURE_DIR / "aneel_siga_geracao.csv").as_uri(),
        "ANEEL_DEC_FEC_URL": (FIXTURE_DIR / "aneel_dec_fec.csv").as_uri(),
        "CCEE_PLD_URL": (FIXTURE_DIR / "ccee_pld_horario_submercado.csv").as_uri(),
        "CCEE_AGENTES_URL": (FIXTURE_DIR / "ccee_agentes_mercado.csv").as_uri(),
        "CCEE_INFOMERCADO_GERACAO_URL": (FIXTURE_DIR / "ccee_infomercado_geracao_horaria_usina.csv").as_uri(),
    }
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("ARTIFACTS_DIR", str(artifacts_dir))
    monkeypatch.setenv("SCHEDULER_ENABLED", str(scheduler_enabled).lower())
    monkeypatch.setenv("SCHEDULER_FORCE_RUN_ON_STARTUP", str(scheduler_force_run_on_startup).lower())
    monkeypatch.setenv("SEED_DEMO_CATALOG", str(seed_demo_catalog).lower())
    for key, value in default_urls.items():
        monkeypatch.setenv(key, value)
    for key, value in (url_overrides or {}).items():
        monkeypatch.setenv(key, value)
    for key, value in (env_overrides or {}).items():
        monkeypatch.setenv(key, value)
    reset_runtime_state()
    upgrade_database("head")
    reset_runtime_state()


def configure_fake_graph_backend(monkeypatch: pytest.MonkeyPatch) -> FakeGraphProjection:
    fake_graph = FakeGraphProjection()
    graph_service = get_graph_service()
    monkeypatch.setattr(graph_service, "project_dataset_version", fake_graph.project_dataset_version)
    monkeypatch.setattr(graph_service, "list_entities", fake_graph.list_entities)
    monkeypatch.setattr(graph_service, "get_entity", fake_graph.get_entity)
    monkeypatch.setattr(graph_service, "get_neighbors", fake_graph.get_neighbors)
    return fake_graph


@pytest.fixture
def workspace_tmp_dir() -> Path:
    TEST_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    runtime_dir = TEST_RUNTIME_DIR / str(uuid4())
    runtime_dir.mkdir(parents=True, exist_ok=True)
    yield runtime_dir
    shutil.rmtree(runtime_dir, ignore_errors=True)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, workspace_tmp_dir: Path) -> TestClient:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    configure_fake_graph_backend(monkeypatch)
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_runtime_state()


@pytest.fixture
def client_without_graph_backend(monkeypatch: pytest.MonkeyPatch, workspace_tmp_dir: Path) -> TestClient:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_runtime_state()


@pytest.fixture
def client_with_copilot(monkeypatch: pytest.MonkeyPatch, workspace_tmp_dir: Path) -> TestClient:
    configure_test_environment(
        monkeypatch,
        workspace_tmp_dir,
        env_overrides={
            "LLM_API_BASE_URL": "https://llm.test/v1",
            "LLM_API_KEY": "test-key",
            "LLM_MODEL": "gpt-test",
        },
    )
    configure_fake_graph_backend(monkeypatch)
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_runtime_state()

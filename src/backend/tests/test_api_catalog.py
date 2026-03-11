from fastapi.testclient import TestClient

from app.db.models import Entity
from app.db.session import get_session_factory


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_catalog_endpoints_use_persisted_data(client: TestClient) -> None:
    sources = client.get("/api/v1/sources")
    assert sources.status_code == 200
    assert sources.json()["total"] == 3

    datasets = client.get("/api/v1/datasets")
    assert datasets.status_code == 200
    assert datasets.json()["total"] == 345

    coverage = client.get("/api/v1/catalog/coverage")
    assert coverage.status_code == 200
    coverage_payload = coverage.json()
    assert coverage_payload["inventoried_total"] == 345
    assert coverage_payload["published_total"] == 8
    assert coverage_payload["documented_only_total"] == 337

    datasets = client.get("/api/v1/datasets", params={"source": "ons", "q": "carga_horaria_submercado"})
    assert datasets.status_code == 200
    payload = datasets.json()
    assert payload["total"] == 1
    dataset_id = payload["items"][0]["id"]
    assert payload["items"][0]["latest_version"] == "2026-03-09"
    assert payload["items"][0]["ingestion_status"] == "published"
    assert payload["items"][0]["adapter_enabled"] is True

    dataset = client.get(f"/api/v1/datasets/{dataset_id}")
    assert dataset.status_code == 200
    assert dataset.json()["refresh_frequency"] == "daily"
    assert dataset.json()["ingestion_status"] == "published"

    documented_only = client.get("/api/v1/datasets", params={"source": "ccee", "q": "PLD_MEDIA_DIARIA"})
    assert documented_only.status_code == 200
    assert documented_only.json()["items"][0]["ingestion_status"] == "documented_only"
    assert documented_only.json()["items"][0]["adapter_enabled"] is False

    versions = client.get(f"/api/v1/datasets/{dataset_id}/versions")
    assert versions.status_code == 200
    assert len(versions.json()["items"]) == 1
    version_id = versions.json()["items"][0]["id"]

    version = client.get(f"/api/v1/datasets/{dataset_id}/versions/{version_id}")
    assert version.status_code == 200
    lineage = version.json()["lineage"]
    assert lineage["source_code"] == "ons"
    assert "artifact_path" in lineage


def test_manual_refresh_returns_accepted(client: TestClient) -> None:
    datasets = client.get("/api/v1/datasets", params={"source": "ons", "q": "carga_horaria_submercado"})
    dataset_id = datasets.json()["items"][0]["id"]

    response = client.post(f"/api/v1/admin/datasets/{dataset_id}/refresh")
    assert response.status_code == 202
    assert response.json()["dataset_id"] == dataset_id
    assert response.json()["status"] in {"queued", "published", "failed"}


def test_documented_only_dataset_cannot_be_refreshed(client: TestClient) -> None:
    datasets = client.get("/api/v1/datasets", params={"source": "ccee", "q": "PLD_MEDIA_DIARIA"})
    dataset_id = datasets.json()["items"][0]["id"]

    response = client.post(f"/api/v1/admin/datasets/{dataset_id}/refresh")
    assert response.status_code == 409
    assert "no ingestion adapter" in response.json()["detail"]


def test_series_graph_and_insights_routes_use_persisted_data(client: TestClient) -> None:
    series = client.get("/api/v1/series", params={"dataset_id": "ds-ons-carga"})
    assert series.status_code == 200
    assert series.json()["items"][0]["metric_code"] == "load_mw"
    assert series.json()["items"][0]["semantic_value_type"] == "observed"
    assert series.json()["items"][0]["reference_time_kind"] == "instant"
    series_id = series.json()["items"][0]["id"]

    observations = client.get(f"/api/v1/series/{series_id}/observations")
    assert observations.status_code == 200
    assert len(observations.json()["items"]) == 3

    entities = client.get("/api/v1/graph/entities", params={"source": "ons", "entity_type": "submarket"})
    assert entities.status_code == 200
    entity_id = entities.json()["items"][0]["id"]
    assert entities.json()["items"][0]["canonical_code"] == "SE-CO"

    entity = client.get(f"/api/v1/graph/entities/{entity_id}")
    assert entity.status_code == 200
    assert entity.json()["entity_type"] == "submarket"

    neighbors = client.get(f"/api/v1/graph/entities/{entity_id}/neighbors")
    assert neighbors.status_code == 200
    assert neighbors.json()["entity_id"] == entity_id
    assert neighbors.json()["provenance"]["dataset_version_ids"]

    overview = client.get("/api/v1/insights/overview")
    assert overview.status_code == 200
    assert len(overview.json()["cards"]) >= 2

    entity_insights = client.get(f"/api/v1/insights/entities/{entity_id}")
    assert entity_insights.status_code == 200
    assert entity_insights.json()["entity_id"] == entity_id

    profile = client.get(f"/api/v1/entities/{entity_id}/profile")
    assert profile.status_code == 200
    assert profile.json()["identity"]["id"] == entity_id
    assert profile.json()["graph_status"] == "available"
    assert profile.json()["neighbors"] is not None
    assert profile.json()["evidence"]


def test_graph_routes_require_backend_when_not_configured(client_without_graph_backend: TestClient) -> None:
    entities = client_without_graph_backend.get("/api/v1/graph/entities")
    assert entities.status_code == 503
    assert "Neo4j" in entities.json()["detail"]

    with get_session_factory()() as session:
        entity_id = session.query(Entity.id).order_by(Entity.name).first()[0]

    profile = client_without_graph_backend.get(f"/api/v1/entities/{entity_id}/profile")
    assert profile.status_code == 200
    assert profile.json()["graph_status"] == "unavailable"
    assert profile.json()["neighbors"] is None

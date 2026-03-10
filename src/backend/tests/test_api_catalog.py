from fastapi.testclient import TestClient


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_catalog_endpoints_use_persisted_data(client: TestClient) -> None:
    sources = client.get("/api/v1/sources")
    assert sources.status_code == 200
    assert sources.json()["total"] == 3

    datasets = client.get("/api/v1/datasets", params={"source": "ons"})
    assert datasets.status_code == 200
    payload = datasets.json()
    assert payload["total"] == 1
    dataset_id = payload["items"][0]["id"]
    assert payload["items"][0]["latest_version"] == "2026-03-09"

    dataset = client.get(f"/api/v1/datasets/{dataset_id}")
    assert dataset.status_code == 200
    assert dataset.json()["refresh_frequency"] == "daily"

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
    datasets = client.get("/api/v1/datasets", params={"source": "ons"})
    dataset_id = datasets.json()["items"][0]["id"]

    response = client.post(f"/api/v1/admin/datasets/{dataset_id}/refresh")
    assert response.status_code == 202
    assert response.json()["dataset_id"] == dataset_id
    assert response.json()["status"] in {"queued", "published", "failed"}


def test_series_graph_and_insights_routes_use_persisted_data(client: TestClient) -> None:
    series = client.get("/api/v1/series", params={"dataset_id": "ds-ons-carga"})
    assert series.status_code == 200
    assert series.json()["items"][0]["metric_code"] == "load_mw"
    series_id = series.json()["items"][0]["id"]

    observations = client.get(f"/api/v1/series/{series_id}/observations")
    assert observations.status_code == 200
    assert len(observations.json()["items"]) == 3

    entities = client.get("/api/v1/graph/entities", params={"source": "ons"})
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


def test_graph_routes_require_backend_when_not_configured(client_without_graph_backend: TestClient) -> None:
    entities = client_without_graph_backend.get("/api/v1/graph/entities")
    assert entities.status_code == 503
    assert "Neo4j" in entities.json()["detail"]

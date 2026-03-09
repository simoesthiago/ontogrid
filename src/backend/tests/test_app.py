from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_core_flow() -> None:
    sources = client.get("/api/v1/sources")
    assert sources.status_code == 200
    assert sources.json()["total"] >= 3

    datasets = client.get("/api/v1/datasets", params={"source": "ons"})
    assert datasets.status_code == 200
    assert datasets.json()["items"][0]["source_code"] == "ons"
    dataset_id = datasets.json()["items"][0]["id"]

    dataset = client.get(f"/api/v1/datasets/{dataset_id}")
    assert dataset.status_code == 200
    assert dataset.json()["id"] == dataset_id

    versions = client.get(f"/api/v1/datasets/{dataset_id}/versions")
    assert versions.status_code == 200
    version_id = versions.json()["items"][0]["id"]

    version = client.get(f"/api/v1/datasets/{dataset_id}/versions/{version_id}")
    assert version.status_code == 200
    assert version.json()["dataset_id"] == dataset_id

    refresh = client.post(f"/api/v1/admin/datasets/{dataset_id}/refresh")
    assert refresh.status_code == 202
    assert refresh.json()["dataset_id"] == dataset_id

    series = client.get("/api/v1/series", params={"dataset_id": dataset_id})
    assert series.status_code == 200
    series_id = series.json()["items"][0]["id"]

    observations = client.get(f"/api/v1/series/{series_id}/observations")
    assert observations.status_code == 200
    assert observations.json()["series_id"] == series_id

    entities = client.get("/api/v1/graph/entities", params={"source": "ons"})
    assert entities.status_code == 200
    entity_id = entities.json()["items"][0]["id"]

    neighbors = client.get(f"/api/v1/graph/entities/{entity_id}/neighbors")
    assert neighbors.status_code == 200
    assert neighbors.json()["entity_id"] == entity_id

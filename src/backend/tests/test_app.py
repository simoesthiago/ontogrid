from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def get_token() -> str:
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "secret"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_core_flow() -> None:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/assets",
        headers=headers,
        json={
            "name": "GB-01",
            "asset_type": "generator",
            "substation_name": "SE Norte",
            "criticality": "high",
            "status": "active",
        },
    )
    assert created.status_code == 201
    asset_id = created.json()["id"]

    job = client.post(
        "/api/v1/ingestion/jobs",
        headers=headers,
        json={
            "source_type": "json_batch",
            "payload_format": "json",
            "records": [
                {
                    "asset_id": asset_id,
                    "measurement_type": "temperature",
                    "value": 96.0,
                    "timestamp": "2026-03-06T12:00:00Z",
                    "quality_flag": "good",
                    "source": "api",
                }
            ],
        },
    )
    assert job.status_code == 202
    assert job.json()["records_accepted"] == 1

    assets = client.get("/api/v1/assets", headers=headers)
    assert assets.status_code == 200
    assert any(item["id"] == asset_id for item in assets.json()["items"])

    health = client.get(f"/api/v1/assets/{asset_id}/health", headers=headers)
    assert health.status_code == 200
    assert health.json()["current"]["score"] < 100

    alerts = client.get("/api/v1/alerts", headers=headers)
    assert alerts.status_code == 200
    assert alerts.json()["total"] >= 1

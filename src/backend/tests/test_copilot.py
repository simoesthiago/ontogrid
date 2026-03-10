from __future__ import annotations

from fastapi.testclient import TestClient

from app.copilot.client import get_llm_client
from app.db.models import CopilotTrace
from app.db.session import get_session_factory


def test_copilot_requires_llm_configuration(client: TestClient) -> None:
    response = client.post("/api/v1/copilot/query", json={"question": "Qual a carga atual?"})
    assert response.status_code == 503
    assert "LLM provider" in response.json()["detail"]


def test_copilot_returns_grounded_response_and_uses_cache(monkeypatch, client_with_copilot: TestClient) -> None:
    llm_client = get_llm_client()
    calls = {"count": 0}

    def fake_complete_json(*, system_prompt: str, user_prompt: str) -> dict[str, object]:
        del system_prompt, user_prompt
        calls["count"] += 1
        return {
            "answer": "A carga publicada mais recente segue concentrada no Sudeste/Centro-Oeste.",
            "follow_up_questions": ["Quero comparar com o Sul."],
        }

    monkeypatch.setattr(llm_client, "complete_json", fake_complete_json)

    payload = {"question": "Qual a carga atual por submercado?", "dataset_ids": ["ds-ons-carga"]}
    first = client_with_copilot.post("/api/v1/copilot/query", json=payload)
    second = client_with_copilot.post("/api/v1/copilot/query", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["count"] == 1
    assert first.json()["citations"]
    assert second.json()["follow_up_questions"] == ["Quero comparar com o Sul."]

    with get_session_factory()() as session:
        assert session.query(CopilotTrace).count() == 2


def test_copilot_reports_insufficient_grounding_without_calling_llm(monkeypatch, client_with_copilot: TestClient) -> None:
    llm_client = get_llm_client()
    calls = {"count": 0}

    def fake_complete_json(*, system_prompt: str, user_prompt: str) -> dict[str, object]:
        del system_prompt, user_prompt
        calls["count"] += 1
        return {"answer": "Nao deveria ser chamado", "follow_up_questions": []}

    monkeypatch.setattr(llm_client, "complete_json", fake_complete_json)

    response = client_with_copilot.post(
        "/api/v1/copilot/query",
        json={
            "question": "Quero um recorte sem dados",
            "dataset_ids": ["ds-ons-carga"],
            "start": "2030-01-01T00:00:00Z",
            "end": "2030-01-02T00:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["citations"] == []
    assert "grounding suficiente" in response.json()["answer"]
    assert calls["count"] == 0

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.session import reset_db_caches
from app.main import create_app


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "app" / "ingestion" / "fixtures"
TEST_RUNTIME_DIR = Path(__file__).resolve().parents[1] / ".tmp" / "test-runtime"


def reset_runtime_state() -> None:
    get_settings.cache_clear()
    reset_db_caches()


def configure_test_environment(
    monkeypatch: pytest.MonkeyPatch,
    runtime_dir: Path,
    *,
    scheduler_enabled: bool = False,
    scheduler_force_run_on_startup: bool = False,
    seed_demo_catalog: bool = True,
    url_overrides: dict[str, str] | None = None,
) -> None:
    db_path = runtime_dir / "ontogrid-test.db"
    artifacts_dir = runtime_dir / "artifacts"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("ARTIFACTS_DIR", str(artifacts_dir))
    monkeypatch.setenv("SCHEDULER_ENABLED", str(scheduler_enabled).lower())
    monkeypatch.setenv("SCHEDULER_FORCE_RUN_ON_STARTUP", str(scheduler_force_run_on_startup).lower())
    monkeypatch.setenv("SEED_DEMO_CATALOG", str(seed_demo_catalog).lower())
    for key, value in (url_overrides or {}).items():
        monkeypatch.setenv(key, value)
    reset_runtime_state()


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
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_runtime_state()

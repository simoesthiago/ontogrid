from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect, select

from app.bootstrap import initialize_application
from app.db.models import Dataset, DatasetVersion, Entity, MetricSeries, Observation, RefreshJob, Source
from app.db.session import get_session_factory
from app.services.refresh_scheduler import RefreshScheduler
from app.services.refresh_service import RefreshService
from tests.conftest import FIXTURE_DIR, configure_test_environment, reset_runtime_state


def _modified_fixture(tmp_path: Path, name: str, content: str) -> str:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path.as_uri()


def test_schema_bootstrap_and_seed(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    runtime = initialize_application()
    try:
        with get_session_factory()() as session:
            inspector = inspect(session.bind)
            assert {
                "source",
                "dataset",
                "dataset_version",
                "refresh_job",
                "entity",
                "entity_alias",
                "relation",
                "metric_series",
                "observation",
                "insight_snapshot",
                "copilot_trace",
            } <= set(inspector.get_table_names())
            assert session.query(Source).count() == 3
            assert session.query(Dataset).count() == 345
            assert session.query(DatasetVersion).count() == 3
            assert session.query(Entity).count() == 3
            assert session.query(MetricSeries).count() == 3
            assert session.query(Observation).count() == 8
    finally:
        runtime.shutdown()
    reset_runtime_state()


def test_refresh_deduplicates_identical_artifact(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(
        monkeypatch,
        workspace_tmp_dir,
        url_overrides={"ONS_CARGA_URL": (FIXTURE_DIR / "ons_carga_horaria_submercado.csv").as_uri()},
    )
    runtime = initialize_application()
    try:
        service = RefreshService(get_session_factory())
        job = service.queue_refresh("ds-ons-carga", trigger_type="manual")
        service.run_refresh(job.id)

        with get_session_factory()() as session:
            versions = session.scalars(
                select(DatasetVersion).where(DatasetVersion.dataset_id == "ds-ons-carga").order_by(DatasetVersion.published_at)
            ).all()
            latest_job = session.scalars(
                select(RefreshJob).where(RefreshJob.id == job.id)
            ).one()
            assert len(versions) == 1
            assert latest_job.status == "published"
            assert latest_job.rows_written == 0
    finally:
        runtime.shutdown()
    reset_runtime_state()


def test_refresh_failure_keeps_last_valid_version(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    runtime = initialize_application()
    try:
        service = RefreshService(get_session_factory())
        from app.ingestion.registry import get_adapter

        ons_adapter = get_adapter("carga_horaria_submercado")
        monkeypatch.setattr(ons_adapter, "fetch_bytes", lambda settings: b"timestamp,submarket\n")
        job = service.queue_refresh("ds-ons-carga", trigger_type="manual")
        service.run_refresh(job.id)

        with get_session_factory()() as session:
            versions = session.scalars(select(DatasetVersion).where(DatasetVersion.dataset_id == "ds-ons-carga")).all()
            failed_job = session.get(RefreshJob, job.id)
            assert len(versions) == 1
            assert failed_job is not None
            assert failed_job.status == "failed"
    finally:
        runtime.shutdown()
    reset_runtime_state()


def test_scheduler_can_trigger_local_refreshes(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(
        monkeypatch,
        workspace_tmp_dir,
        url_overrides={
            "ONS_CARGA_URL": _modified_fixture(
                workspace_tmp_dir,
                "ons.csv",
                "timestamp,submarket,load_mw\n2026-03-10T00:00:00Z,Sudeste/Centro-Oeste,82000.0\n",
            ),
            "ANEEL_TARIFAS_URL": _modified_fixture(
                workspace_tmp_dir,
                "aneel.csv",
                "cycle_start,cycle_end,distributor,tariff_rs_mwh\n2026-04-01T00:00:00Z,2026-04-30T23:59:59Z,Enel SP,420.0\n",
            ),
            "CCEE_PLD_URL": _modified_fixture(
                workspace_tmp_dir,
                "ccee.csv",
                "timestamp,submarket,pld_rs_mwh\n2026-03-10T00:00:00Z,Sudeste/Centro-Oeste,191.4\n",
            ),
        },
    )
    runtime = initialize_application()
    try:
        service = RefreshService(get_session_factory())
        scheduler = RefreshScheduler(service.run_due_refreshes, poll_interval_seconds=60)
        runs = scheduler.run_once(force=True)

        with get_session_factory()() as session:
            assert runs == 3
            assert session.query(DatasetVersion).count() == 6
            assert session.query(Observation).count() == 11
    finally:
        runtime.shutdown()
    reset_runtime_state()

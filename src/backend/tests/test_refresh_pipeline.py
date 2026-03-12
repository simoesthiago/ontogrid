from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import inspect, select

from app.bootstrap import initialize_application
from app.db.models import (
    Dataset,
    DatasetVersion,
    Entity,
    EntityAlias,
    EvidenceRegistry,
    HarmonizationEvent,
    MetricSeries,
    Observation,
    RefreshJob,
    SeriesRegistry,
    Source,
)
from app.db.session import get_session_factory
from app.ingestion.base import (
    ParsedDatasetPayload,
    ParsedDatasetVersion,
    ParsedEntity,
    ParsedMetricSeries,
    ParsedObservation,
)
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
                "party_master",
                "agent_profile_master",
                "asset_master_generation",
                "asset_bridge_generation",
                "geo_electric_master",
                "series_registry",
                "evidence_registry",
                "harmonization_event",
            } <= set(inspector.get_table_names())
            assert session.query(Source).count() == 3
            assert session.query(Dataset).count() == 345
            assert session.query(DatasetVersion).count() == 11
            assert session.query(Entity).count() == 14
            assert session.query(MetricSeries).count() == 11
            assert session.query(SeriesRegistry).count() == 11
            assert session.query(Observation).count() == 30
            assert session.query(HarmonizationEvent).count() == 38
            assert session.query(EvidenceRegistry).count() > session.query(Observation).count()
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
            assert runs == 11
            assert session.query(DatasetVersion).count() == 14
            assert session.query(Observation).count() == 33
    finally:
        runtime.shutdown()
    reset_runtime_state()


def test_harmonization_merges_agents_by_exact_tax_id_and_plants_by_exact_ceg(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    runtime = initialize_application()
    try:
        with get_session_factory()() as session:
            agent_entities = session.scalars(select(Entity).where(Entity.entity_type == "agent").order_by(Entity.name)).all()
            plant_entities = session.scalars(select(Entity).where(Entity.entity_type == "plant").order_by(Entity.name)).all()

            assert len(agent_entities) == 3
            assert len(plant_entities) == 2

            itaipu_agent = session.scalar(select(Entity).where(Entity.name == "Itaipu Binacional", Entity.entity_type == "agent"))
            itaipu_plant = session.scalar(select(Entity).where(Entity.name == "UHE Itaipu", Entity.entity_type == "plant"))
            assert itaipu_agent is not None
            assert itaipu_plant is not None

            agent_rules = session.scalars(
                select(HarmonizationEvent.match_rule).where(HarmonizationEvent.entity_id == itaipu_agent.id)
            ).all()
            plant_rules = session.scalars(
                select(HarmonizationEvent.match_rule).where(HarmonizationEvent.entity_id == itaipu_plant.id)
            ).all()

            assert "exact_tax_id" in agent_rules
            assert "exact_ceg" in plant_rules
    finally:
        runtime.shutdown()
    reset_runtime_state()


def test_approximate_match_does_not_create_public_alias(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    runtime = initialize_application()
    try:
        from app.ingestion.registry import get_adapter

        updated_fixture = (
            "reference_month,agent_code,legal_name,tax_id,agent_class,status,state\n"
            "2026-04-01T00:00:00Z,,Furnazz,,gerador,active,RJ\n"
        ).encode("utf-8")
        adapter = get_adapter("agentes_mercado_ccee")
        monkeypatch.setattr(adapter, "fetch_bytes", lambda settings: updated_fixture)

        service = RefreshService(get_session_factory())
        job = service.queue_refresh("ds-ccee-agentes", trigger_type="manual")
        service.run_refresh(job.id)

        with get_session_factory()() as session:
            furnas = session.scalar(select(Entity).where(Entity.entity_type == "agent", Entity.name == "Furnas"))
            furnazz = session.scalar(select(Entity).where(Entity.entity_type == "agent", Entity.name == "Furnazz"))
            assert furnas is not None
            assert furnazz is not None
            assert furnas.id != furnazz.id

            furnas_aliases = session.scalars(
                select(EntityAlias.alias_name).where(EntityAlias.entity_id == furnas.id).order_by(EntityAlias.alias_name)
            ).all()
            assert "Furnazz" not in furnas_aliases
    finally:
        runtime.shutdown()
    reset_runtime_state()


def test_series_with_different_semantics_do_not_collapse_same_metric_series(monkeypatch, workspace_tmp_dir: Path) -> None:
    configure_test_environment(monkeypatch, workspace_tmp_dir)
    runtime = initialize_application()
    try:
        from app.ingestion.registry import get_adapter

        adapter = get_adapter("carga_horaria_submercado")
        monkeypatch.setattr(adapter, "fetch_bytes", lambda settings: b"semantic-series-test")

        def parse_with_two_semantics(raw_bytes: bytes, checksum: str) -> ParsedDatasetPayload:
            del raw_bytes
            observed_at = datetime(2026, 3, 10, 0, 0, tzinfo=timezone.utc)
            return ParsedDatasetPayload(
                dataset_version=ParsedDatasetVersion(
                    label="2026-03-10",
                    extracted_at=observed_at,
                    published_at=observed_at,
                    coverage_start=observed_at,
                    coverage_end=observed_at,
                    row_count=2,
                    schema_version="v1",
                    checksum=checksum,
                ),
                entities=[
                    ParsedEntity(
                        key="submarket:SE-CO",
                        entity_type="submarket",
                        canonical_code="SE-CO",
                        name="Sudeste/Centro-Oeste",
                        jurisdiction="SIN",
                        attributes={"source_code": "ons", "operator_code": "SE-CO"},
                    )
                ],
                metric_series=[
                    ParsedMetricSeries(
                        key="series:load_observed",
                        metric_code="load_mw",
                        metric_name="Carga observada",
                        unit="MW",
                        temporal_granularity="hour",
                        entity_type="submarket",
                        semantic_value_type="observed",
                        reference_time_kind="instant",
                    ),
                    ParsedMetricSeries(
                        key="series:load_accounted",
                        metric_code="load_mw",
                        metric_name="Carga contabilizada",
                        unit="MW",
                        temporal_granularity="hour",
                        entity_type="submarket",
                        semantic_value_type="accounted",
                        reference_time_kind="instant",
                    ),
                ],
                observations=[
                    ParsedObservation(
                        series_key="series:load_observed",
                        entity_key="submarket:SE-CO",
                        time=observed_at,
                        value_numeric=82000.0,
                        published_at=observed_at,
                    ),
                    ParsedObservation(
                        series_key="series:load_accounted",
                        entity_key="submarket:SE-CO",
                        time=observed_at,
                        value_numeric=81950.0,
                        published_at=observed_at,
                    ),
                ],
            )

        monkeypatch.setattr(adapter, "parse", parse_with_two_semantics)

        service = RefreshService(get_session_factory())
        job = service.queue_refresh("ds-ons-carga", trigger_type="manual")
        service.run_refresh(job.id)

        with get_session_factory()() as session:
            series = session.scalars(
                select(MetricSeries)
                .where(MetricSeries.dataset_id == "ds-ons-carga", MetricSeries.metric_code == "load_mw")
                .order_by(MetricSeries.semantic_value_type)
            ).all()
            assert len(series) == 2
            assert {(row.semantic_value_type, row.reference_time_kind) for row in series} == {
                ("accounted", "instant"),
                ("observed", "instant"),
            }
    finally:
        runtime.shutdown()
    reset_runtime_state()

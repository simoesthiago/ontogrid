from app.ingestion.adapters.aneel import AneelAgentesGeracaoAdapter, AneelTarifasAdapter
from app.ingestion.adapters.ccee import CceePldAdapter, CceePldMediaDiariaAdapter
from app.ingestion.adapters.ons import OnsCargaAdapter, OnsCargaDiariaAdapter


def test_ons_adapter_parses_fixture() -> None:
    adapter = OnsCargaAdapter()
    raw_bytes = adapter.bootstrap_bytes()
    parsed = adapter.parse(raw_bytes, adapter.checksum(raw_bytes))
    assert parsed.dataset_version.label == "2026-03-09"
    assert parsed.dataset_version.row_count == 3
    assert len(parsed.entities) == 1
    assert len(parsed.metric_series) == 1
    assert len(parsed.observations) == 3


def test_aneel_adapter_parses_fixture() -> None:
    adapter = AneelTarifasAdapter()
    raw_bytes = adapter.bootstrap_bytes()
    parsed = adapter.parse(raw_bytes, adapter.checksum(raw_bytes))
    assert parsed.dataset_version.label == "2026-03"
    assert parsed.dataset_version.row_count == 2
    assert len(parsed.entities) == 2
    assert len(parsed.metric_series) == 1
    assert len(parsed.observations) == 2


def test_ccee_adapter_parses_fixture() -> None:
    adapter = CceePldAdapter()
    raw_bytes = adapter.bootstrap_bytes()
    parsed = adapter.parse(raw_bytes, adapter.checksum(raw_bytes))
    assert parsed.dataset_version.label == "2026-03-09"
    assert parsed.dataset_version.row_count == 3
    assert len(parsed.entities) == 1
    assert len(parsed.metric_series) == 1
    assert len(parsed.observations) == 3


def test_new_adapter_candidates_parse_fixtures() -> None:
    ons_daily = OnsCargaDiariaAdapter()
    raw_bytes = ons_daily.bootstrap_bytes()
    parsed = ons_daily.parse(raw_bytes, ons_daily.checksum(raw_bytes))
    assert parsed.dataset_version.label == "2026-03-09"
    assert len(parsed.observations) == 4

    aneel_agents = AneelAgentesGeracaoAdapter()
    raw_bytes = aneel_agents.bootstrap_bytes()
    parsed = aneel_agents.parse(raw_bytes, aneel_agents.checksum(raw_bytes))
    assert parsed.dataset_version.label == "2026-03"
    assert len(parsed.entities) == 2
    assert len(parsed.metric_series) == 1

    ccee_daily = CceePldMediaDiariaAdapter()
    raw_bytes = ccee_daily.bootstrap_bytes()
    parsed = ccee_daily.parse(raw_bytes, ccee_daily.checksum(raw_bytes))
    assert parsed.dataset_version.label == "2026-03-09"
    assert len(parsed.observations) == 4

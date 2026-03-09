from app.ingestion.adapters.aneel import AneelTarifasAdapter
from app.ingestion.adapters.ccee import CceePldAdapter
from app.ingestion.adapters.ons import OnsCargaAdapter


def test_ons_adapter_parses_fixture() -> None:
    adapter = OnsCargaAdapter()
    raw_bytes = adapter.bootstrap_bytes()
    parsed = adapter.parse(raw_bytes, adapter.checksum(raw_bytes))
    assert parsed.label == "2026-03-09"
    assert parsed.row_count == 3


def test_aneel_adapter_parses_fixture() -> None:
    adapter = AneelTarifasAdapter()
    raw_bytes = adapter.bootstrap_bytes()
    parsed = adapter.parse(raw_bytes, adapter.checksum(raw_bytes))
    assert parsed.label == "2026-03"
    assert parsed.row_count == 2


def test_ccee_adapter_parses_fixture() -> None:
    adapter = CceePldAdapter()
    raw_bytes = adapter.bootstrap_bytes()
    parsed = adapter.parse(raw_bytes, adapter.checksum(raw_bytes))
    assert parsed.label == "2026-03-09"
    assert parsed.row_count == 3

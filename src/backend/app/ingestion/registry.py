from __future__ import annotations

from app.ingestion.adapters import AneelTarifasAdapter, CceePldAdapter, OnsCargaAdapter
from app.ingestion.base import BaseDatasetAdapter

_ADAPTERS: dict[str, BaseDatasetAdapter] = {
    "carga_horaria_submercado": OnsCargaAdapter(),
    "tarifas_distribuicao": AneelTarifasAdapter(),
    "pld_horario_submercado": CceePldAdapter(),
}


def has_adapter(dataset_code: str) -> bool:
    return dataset_code in _ADAPTERS


def list_adapter_codes() -> set[str]:
    return set(_ADAPTERS.keys())


def get_adapter(dataset_code: str) -> BaseDatasetAdapter:
    try:
        return _ADAPTERS[dataset_code]
    except KeyError as exc:
        raise KeyError(f"No adapter registered for dataset {dataset_code}") from exc

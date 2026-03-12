from __future__ import annotations

from app.ingestion.adapters import (
    AneelDecFecAdapter,
    AneelAgentesGeracaoAdapter,
    AneelSigaAdapter,
    AneelTarifasAdapter,
    CceeAgentesAdapter,
    CceeInfomercadoGeracaoAdapter,
    CceePldMediaDiariaAdapter,
    CceePldAdapter,
    OnsCargaAdapter,
    OnsCargaDiariaAdapter,
    OnsGeracaoUsinaAdapter,
)
from app.ingestion.base import BaseDatasetAdapter

_ADAPTERS: dict[str, BaseDatasetAdapter] = {
    "carga_horaria_submercado": OnsCargaAdapter(),
    "geracao_usina_horaria": OnsGeracaoUsinaAdapter(),
    "carga_energia_diaria": OnsCargaDiariaAdapter(),
    "siga_geracao_aneel": AneelSigaAdapter(),
    "tarifas_distribuicao": AneelTarifasAdapter(),
    "indicadores_dec_fec": AneelDecFecAdapter(),
    "agentes_geracao_aneel": AneelAgentesGeracaoAdapter(),
    "pld_horario_submercado": CceePldAdapter(),
    "pld_media_diaria": CceePldMediaDiariaAdapter(),
    "agentes_mercado_ccee": CceeAgentesAdapter(),
    "infomercado_geracao_horaria_usina": CceeInfomercadoGeracaoAdapter(),
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

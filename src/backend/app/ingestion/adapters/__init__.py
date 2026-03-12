from app.ingestion.adapters.aneel import (
    AneelAgentesGeracaoAdapter,
    AneelDecFecAdapter,
    AneelSigaAdapter,
    AneelTarifasAdapter,
)
from app.ingestion.adapters.ccee import (
    CceeAgentesAdapter,
    CceeInfomercadoGeracaoAdapter,
    CceePldAdapter,
    CceePldMediaDiariaAdapter,
)
from app.ingestion.adapters.ons import OnsCargaAdapter, OnsCargaDiariaAdapter, OnsGeracaoUsinaAdapter

__all__ = [
    "AneelAgentesGeracaoAdapter",
    "AneelDecFecAdapter",
    "AneelSigaAdapter",
    "AneelTarifasAdapter",
    "CceeAgentesAdapter",
    "CceeInfomercadoGeracaoAdapter",
    "CceePldAdapter",
    "CceePldMediaDiariaAdapter",
    "OnsCargaAdapter",
    "OnsCargaDiariaAdapter",
    "OnsGeracaoUsinaAdapter",
]

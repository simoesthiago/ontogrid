from app.ingestion.adapters.aneel import AneelDecFecAdapter, AneelSigaAdapter, AneelTarifasAdapter
from app.ingestion.adapters.ccee import CceeAgentesAdapter, CceeInfomercadoGeracaoAdapter, CceePldAdapter
from app.ingestion.adapters.ons import OnsCargaAdapter, OnsGeracaoUsinaAdapter

__all__ = [
    "AneelDecFecAdapter",
    "AneelSigaAdapter",
    "AneelTarifasAdapter",
    "CceeAgentesAdapter",
    "CceeInfomercadoGeracaoAdapter",
    "CceePldAdapter",
    "OnsCargaAdapter",
    "OnsGeracaoUsinaAdapter",
]

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Dataset, Source

SOURCE_SEEDS = [
    {
        "id": "src-aneel",
        "code": "aneel",
        "name": "ANEEL",
        "authority_type": "regulator",
        "refresh_strategy": "scheduled_download",
        "status": "active",
    },
    {
        "id": "src-ons",
        "code": "ons",
        "name": "ONS",
        "authority_type": "system_operator",
        "refresh_strategy": "scheduled_download",
        "status": "active",
    },
    {
        "id": "src-ccee",
        "code": "ccee",
        "name": "CCEE",
        "authority_type": "market_operator",
        "refresh_strategy": "scheduled_download",
        "status": "active",
    },
]

DATASET_SEEDS = [
    {
        "id": "ds-ons-carga",
        "source_id": "src-ons",
        "code": "carga_horaria_submercado",
        "name": "Carga horaria por submercado",
        "domain": "operacao",
        "description": "Serie horaria curada a partir do portal publico do ONS.",
        "granularity": "hour",
        "refresh_frequency": "daily",
        "schema_summary": {"dimensions": ["submarket"], "metrics": ["load_mw"]},
    },
    {
        "id": "ds-aneel-tarifas",
        "source_id": "src-aneel",
        "code": "tarifas_distribuicao",
        "name": "Tarifas homologadas de distribuicao",
        "domain": "regulatorio",
        "description": "Base publica harmonizada de tarifas e ciclos homologatorios.",
        "granularity": "month",
        "refresh_frequency": "monthly",
        "schema_summary": {"dimensions": ["distributor"], "metrics": ["tariff_rs_mwh"]},
    },
    {
        "id": "ds-ccee-pld",
        "source_id": "src-ccee",
        "code": "pld_horario_submercado",
        "name": "PLD horario por submercado",
        "domain": "mercado",
        "description": "Serie publica do preco de liquidacao das diferencas por submercado.",
        "granularity": "hour",
        "refresh_frequency": "daily",
        "schema_summary": {"dimensions": ["submarket"], "metrics": ["pld_rs_mwh"]},
    },
]


def seed_reference_catalog(session: Session) -> None:
    existing_source_ids = set(session.scalars(select(Source.id)).all())
    for payload in SOURCE_SEEDS:
        if payload["id"] not in existing_source_ids:
            session.add(Source(**payload))

    existing_dataset_ids = set(session.scalars(select(Dataset.id)).all())
    for payload in DATASET_SEEDS:
        if payload["id"] not in existing_dataset_ids:
            session.add(Dataset(**payload))

    session.commit()

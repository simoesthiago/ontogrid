from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_inventory import get_dataset_seeds, get_source_seeds
from app.db.models import AppUser, Dataset, Source


def seed_reference_catalog(session: Session) -> None:
    if session.get(AppUser, "demo-user") is None:
        session.add(
            AppUser(
                id="demo-user",
                email=None,
                display_name="Demo User",
            )
        )

    existing_source_ids = set(session.scalars(select(Source.id)).all())
    for payload in get_source_seeds():
        if payload["id"] not in existing_source_ids:
            session.add(Source(**payload))

    existing_dataset_ids = set(session.scalars(select(Dataset.id)).all())
    for payload in get_dataset_seeds():
        if payload.id not in existing_dataset_ids:
            session.add(
                Dataset(
                    id=payload.id,
                    source_id=payload.source_id,
                    code=payload.code,
                    name=payload.name,
                    domain=payload.domain,
                    description=payload.description,
                    granularity=payload.granularity,
                    refresh_frequency=payload.refresh_frequency,
                    schema_summary=payload.schema_summary,
                )
            )

    session.commit()

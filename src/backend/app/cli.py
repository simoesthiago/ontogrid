from __future__ import annotations

import argparse

from sqlalchemy import select

from app.core.config import get_settings
from app.db.migrations import upgrade_database
from app.db.models import Dataset
from app.db.seed import seed_reference_catalog
from app.db.session import get_session_factory
from app.ingestion.registry import has_adapter
from app.services.refresh_service import RefreshService


def bootstrap_catalog() -> None:
    upgrade_database("head")
    with get_session_factory()() as session:
        seed_reference_catalog(session)


def bootstrap_sample_data() -> None:
    bootstrap_catalog()
    RefreshService(get_session_factory()).refresh_missing_versions(use_fixtures=True)


def bootstrap_selected_live_data(dataset_codes: list[str] | None = None) -> None:
    bootstrap_catalog()
    settings = get_settings()
    selected_codes = dataset_codes or settings.bootstrap_dataset_code_list
    if not selected_codes:
        raise ValueError("BOOTSTRAP_DATASET_CODES must be provided for selected_live mode")

    with get_session_factory()() as session:
        datasets = session.scalars(select(Dataset).where(Dataset.code.in_(selected_codes)).order_by(Dataset.code)).all()
        datasets_by_code = {dataset.code: dataset for dataset in datasets}

    missing_codes = [code for code in selected_codes if code not in datasets_by_code]
    if missing_codes:
        raise ValueError(f"Unknown dataset codes for selected_live mode: {', '.join(sorted(missing_codes))}")

    unsupported_codes = [code for code in selected_codes if not has_adapter(code)]
    if unsupported_codes:
        raise ValueError(f"Datasets without ingestion adapter: {', '.join(sorted(unsupported_codes))}")

    refresh_service = RefreshService(get_session_factory())
    for dataset_code in selected_codes:
        job = refresh_service.queue_refresh(datasets_by_code[dataset_code].id, trigger_type="manual")
        refresh_service.run_refresh(job.id, bootstrap=False)


def bootstrap_live_data() -> None:
    bootstrap_catalog()
    RefreshService(get_session_factory()).refresh_missing_versions(use_fixtures=False)


def bootstrap_runtime() -> None:
    settings = get_settings()
    mode = settings.bootstrap_mode.strip().lower()

    if mode == "catalog":
        bootstrap_catalog()
        return
    if mode == "sample":
        bootstrap_sample_data()
        return
    if mode == "selected_live":
        bootstrap_selected_live_data()
        return
    raise ValueError(f"Unsupported BOOTSTRAP_MODE: {settings.bootstrap_mode}")


def main() -> None:
    parser = argparse.ArgumentParser(description="OntoGrid backend operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("bootstrap", help="Apply the bootstrap mode configured by BOOTSTRAP_MODE")
    subparsers.add_parser("bootstrap-catalog", help="Apply migrations and seed the full catalog without ingesting data")
    subparsers.add_parser("bootstrap-sample-data", help="Apply migrations, seed the catalog, and ingest sample fixtures")
    subparsers.add_parser(
        "bootstrap-selected-live-data",
        help="Apply migrations, seed the catalog, and ingest only BOOTSTRAP_DATASET_CODES from live sources",
    )
    subparsers.add_parser(
        "bootstrap-live-data",
        help="Apply migrations, seed the catalog, and fetch missing live data for every adapter-enabled dataset",
    )
    args = parser.parse_args()

    if args.command == "bootstrap":
        bootstrap_runtime()
    elif args.command == "bootstrap-catalog":
        bootstrap_catalog()
    elif args.command == "bootstrap-sample-data":
        bootstrap_sample_data()
    elif args.command == "bootstrap-selected-live-data":
        bootstrap_selected_live_data()
    elif args.command == "bootstrap-live-data":
        bootstrap_live_data()


if __name__ == "__main__":
    main()

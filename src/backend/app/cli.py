from __future__ import annotations

import argparse

from app.db.migrations import upgrade_database
from app.db.seed import seed_reference_catalog
from app.db.session import get_session_factory
from app.services.refresh_service import RefreshService


def bootstrap_live_data() -> None:
    upgrade_database("head")
    with get_session_factory()() as session:
        seed_reference_catalog(session)
    RefreshService(get_session_factory()).refresh_missing_versions(use_fixtures=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="OntoGrid backend operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("bootstrap-live-data", help="Apply migrations, seed the catalog, and fetch missing live data")
    args = parser.parse_args()

    if args.command == "bootstrap-live-data":
        bootstrap_live_data()


if __name__ == "__main__":
    main()

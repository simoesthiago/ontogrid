from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_alembic_config() -> Config:
    root = _backend_root()
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    return config


def upgrade_database(revision: str = "head") -> None:
    command.upgrade(get_alembic_config(), revision)

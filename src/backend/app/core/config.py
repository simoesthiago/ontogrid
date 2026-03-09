from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OntoGrid API"
    app_env: str = "development"
    database_url: str = "sqlite:///./ontogrid.db"
    artifacts_dir: str = "./data/artifacts"
    seed_demo_catalog: bool = True
    scheduler_enabled: bool = False
    scheduler_poll_interval_seconds: int = 300
    scheduler_force_run_on_startup: bool = False
    ons_carga_url: str = ""
    aneel_tarifas_url: str = ""
    ccee_pld_url: str = ""
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    token_expiration_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def normalized_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def artifacts_path(self) -> Path:
        return Path(self.artifacts_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()

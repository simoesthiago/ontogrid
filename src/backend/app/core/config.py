from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OntoGrid API"
    app_env: str = "development"
    database_url: str = "sqlite:///./ontogrid.db"
    artifacts_dir: str = "./data/artifacts"
    bootstrap_mode: str = "sample"
    bootstrap_dataset_codes: str = ""
    seed_demo_catalog: bool = False
    scheduler_enabled: bool = False
    scheduler_poll_interval_seconds: int = 300
    scheduler_force_run_on_startup: bool = False
    redis_url: str = ""
    neo4j_uri: str = ""
    neo4j_username: str = ""
    neo4j_password: str = ""
    llm_api_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    copilot_cache_ttl_seconds: int = 3600
    ons_carga_url: str = ""
    ons_ckan_base_url: str = "https://dados.ons.org.br"
    ons_carga_package_id: str = "curva-de-carga-horaria"
    ons_carga_resource_id: str = ""
    ons_geracao_usina_url: str = ""
    ons_geracao_usina_package_id: str = "geracao-por-usina-em-base-horaria"
    ons_geracao_usina_resource_id: str = ""
    ons_carga_diaria_url: str = ""
    ons_carga_diaria_package_id: str = "carga-de-energia-diaria"
    ons_carga_diaria_resource_id: str = ""
    aneel_tarifas_url: str = ""
    aneel_ckan_base_url: str = "https://dadosabertos.aneel.gov.br"
    aneel_tarifas_package_id: str = "tarifas-distribuidoras-energia-eletrica"
    aneel_tarifas_resource_id: str = ""
    aneel_siga_url: str = ""
    aneel_siga_package_id: str = "siga-sistema-de-informacoes-de-geracao-da-aneel"
    aneel_siga_resource_id: str = ""
    aneel_dec_fec_url: str = ""
    aneel_dec_fec_package_id: str = "indicadores-coletivos-de-continuidade-dec-e-fec"
    aneel_dec_fec_resource_id: str = ""
    aneel_agentes_geracao_url: str = ""
    aneel_agentes_geracao_package_id: str = "agentes-de-geracao-de-energia-eletrica"
    aneel_agentes_geracao_resource_id: str = ""
    ccee_pld_url: str = ""
    ccee_ckan_base_url: str = "https://dadosabertos.ccee.org.br"
    ccee_pld_package_id: str = "PLD_HORARIO"
    ccee_pld_resource_id: str = ""
    ccee_pld_media_diaria_url: str = ""
    ccee_pld_media_diaria_package_id: str = "PLD_MEDIA_DIARIA"
    ccee_pld_media_diaria_resource_id: str = ""
    ccee_agentes_url: str = ""
    ccee_agentes_package_id: str = "LISTA_AGENTE_ASSOCIADO"
    ccee_agentes_resource_id: str = ""
    ccee_infomercado_geracao_url: str = ""
    ccee_infomercado_geracao_package_id: str = "GERACAO_HORARIA_USINA"
    ccee_infomercado_geracao_resource_id: str = ""
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

    @property
    def bootstrap_dataset_code_list(self) -> list[str]:
        return [item.strip() for item in self.bootstrap_dataset_codes.split(",") if item.strip()]

    @property
    def neo4j_enabled(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_username and self.neo4j_password)

    @property
    def redis_enabled(self) -> bool:
        return bool(self.redis_url)

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_base_url and self.llm_api_key and self.llm_model)


@lru_cache
def get_settings() -> Settings:
    return Settings()

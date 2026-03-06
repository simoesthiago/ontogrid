from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OntoGrid API"
    app_env: str = "development"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    token_expiration_seconds: int = 3600
    demo_tenant_id: str = "11111111-1111-1111-1111-111111111111"
    demo_user_id: str = "22222222-2222-2222-2222-222222222222"
    demo_user_email: str = "admin@example.com"
    demo_user_password: str = "secret"
    demo_user_role: str = "admin"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()

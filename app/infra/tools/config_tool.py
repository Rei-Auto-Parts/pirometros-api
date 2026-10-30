from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracao por variaveis de ambiente (ou `.env` local, ignorado pelo git)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: SecretStr
    port: int = 8000
    log_level: str = "INFO"
    run_migrations_on_start: bool = True

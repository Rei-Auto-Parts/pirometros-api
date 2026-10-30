from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def run_migrations(database_url: str) -> None:
    """Aplica as migrations do schema `app`. Nunca toca `public.receiver_data`."""
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    # Pela `attributes` e nao por `set_main_option`: o configparser trata `%` da senha.
    config.attributes["url"] = database_url
    command.upgrade(config, "head")

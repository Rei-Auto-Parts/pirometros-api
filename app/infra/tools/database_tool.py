from __future__ import annotations

from sqlalchemy import Engine, create_engine


def build_engine(database_url: str) -> Engine:
    """Engine preguicosa: so conecta na primeira consulta. O timeout evita health pendurado."""
    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )

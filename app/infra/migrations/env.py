"""Ambiente do Alembic. Versiona somente o schema `app`.

`public.receiver_data` pertence ao sincronizador: o `include_object` abaixo faz o Alembic
ignorar qualquer objeto fora do schema `app`, e o `CREATE SCHEMA` precede a tabela de versao
porque ela tambem mora em `app` (o Alembic a cria antes da primeira migration).
"""

import os

from alembic import context
from sqlalchemy import create_engine, pool, text

SCHEMA = "app"
# Sem modelos ainda. Quando houver, use `MetaData(schema="app")`.
target_metadata = None


def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        return obj.schema == SCHEMA
    return True


def run_migrations_online() -> None:
    url = context.config.attributes.get("url") or os.environ["DATABASE_URL"]
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=SCHEMA,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("modo offline nao suportado: rode contra o banco")
run_migrations_online()

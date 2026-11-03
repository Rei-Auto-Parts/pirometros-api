"""Cria `public.receiver_data` so no Postgres descartavel do compose, para os testes it e bdd.

Em producao a tabela e do sincronizador: nada aqui roda fora dos testes, e a guarda abaixo
recusa qualquer banco que nao seja o servico `postgres` do compose.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine, text
from sqlalchemy.engine import make_url

from infra.tools.database_tool import build_engine

COMPOSE_HOST = "postgres"

DDL = (
    """
    CREATE TABLE IF NOT EXISTS public.receiver_data (
        id               integer PRIMARY KEY,
        gtw_id           varchar(14),
        gtw_name         varchar(6),
        dev_id           varchar(14),
        dev_name         varchar(6),
        reg_date         timestamp,
        reg_thermocouple varchar(6),
        reg_unit         varchar(10),
        reg_tcj          double precision,
        reg_read_delay   integer,
        reg_place        integer,
        reg_battery      integer,
        reg_temperature  integer,
        reg_detect_time  double precision,
        synced_at        timestamptz NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_receiver_data_date ON public.receiver_data (reg_date)",
    "CREATE INDEX IF NOT EXISTS idx_receiver_data_dev ON public.receiver_data (dev_id, reg_date)",
)

INSERT_READING = text("""
    INSERT INTO public.receiver_data (
        id, gtw_id, gtw_name, dev_id, dev_name, reg_date, reg_thermocouple, reg_unit,
        reg_tcj, reg_read_delay, reg_place, reg_battery, reg_temperature, reg_detect_time
    ) VALUES (
        :id, 'B571.430C.0000', :gateway_name, :dev_id, :dev_name, :measured_at, 'S', 'Celsius',
        31.4, 0, :place, :battery, :temperature, 3.9
    )
    """)

INSERT_GENERATED = text("""
    INSERT INTO public.receiver_data (
        id, gtw_id, gtw_name, dev_id, dev_name, reg_date, reg_thermocouple, reg_unit,
        reg_tcj, reg_read_delay, reg_place, reg_battery, reg_temperature, reg_detect_time
    )
    SELECT 100000 + n, 'B571.430C.0000', 'RERF ', 'C24C.F90D.0000', 'PI-12',
           CAST(:day AS timestamp) + n * interval '5 seconds', 'S', 'Celsius',
           31.4, 0, 60, 63, 1400 + n % 300, 3.9
    FROM generate_series(1, :count) AS n
    """)


def build_test_engine(database_url: str) -> Engine:
    """Engine do banco descartavel, com a tabela criada. Aborta fora do compose."""
    host = make_url(database_url).host
    if host != COMPOSE_HOST:
        raise RuntimeError(
            f"a fixture so roda no Postgres descartavel do compose ('{COMPOSE_HOST}'), "
            f"nao em '{host}'"
        )
    engine = build_engine(database_url)
    with engine.begin() as connection:
        for statement in DDL:
            connection.execute(text(statement))
    return engine


def clear_readings(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE public.receiver_data"))


def insert_reading(
    engine: Engine,
    reading_id: int,
    measured_at: datetime,
    dev_id: str = "C24C.F90D.0000",
    dev_name: str = "PI-12",
    temperature: int = 1548,
    place: int = 60,
    battery: int = 63,
    gateway_name: str = "RERF ",
) -> None:
    with engine.begin() as connection:
        connection.execute(
            INSERT_READING,
            {
                "id": reading_id,
                "gateway_name": gateway_name,
                "dev_id": dev_id,
                "dev_name": dev_name,
                "measured_at": measured_at,
                "place": place,
                "battery": battery,
                "temperature": temperature,
            },
        )


def insert_generated(engine: Engine, count: int, day: datetime) -> None:
    """`count` leituras do PI-12, uma a cada 5 segundos a partir de `day`."""
    with engine.begin() as connection:
        connection.execute(INSERT_GENERATED, {"day": day, "count": count})


def snapshot_readings(engine: Engine) -> list[tuple[object, ...]]:
    with engine.connect() as connection:
        rows = connection.execute(text("SELECT * FROM public.receiver_data ORDER BY id"))
        return [tuple(row) for row in rows]

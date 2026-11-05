from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import Engine, TextClause, text

from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.reading_dto import ReadingDto

COLUMNS = (
    "id, gtw_id, gtw_name, dev_id, dev_name, reg_date, reg_thermocouple, reg_unit, reg_tcj, "
    "reg_read_delay, reg_place, reg_battery, reg_temperature, reg_detect_time"
)
# Leitura sem temperatura nunca sai da API: total e paginacao so contam as que tem.
PERIOD_FILTER = "reg_date BETWEEN :start AND :end AND reg_temperature IS NOT NULL"
PYROMETER_FILTER = " AND dev_id = ANY(:ids)"


class ReadingRepository:
    """So le `public.receiver_data`: toda consulta e um SELECT com colunas explicitas."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def find_readings(
        self,
        start: datetime,
        end: datetime,
        pyrometer_ids: Sequence[str],
        limit: int,
        offset: int,
    ) -> list[ReadingDto]:
        where, params = self._filter(start, end, pyrometer_ids)
        statement = text(
            f"SELECT {COLUMNS} FROM public.receiver_data WHERE {where} "
            "ORDER BY reg_date DESC, id DESC LIMIT :limit OFFSET :offset"
        )
        rows = self._fetch(statement, {**params, "limit": limit, "offset": offset})
        return [self._to_reading(row) for row in rows]

    def count_readings(self, start: datetime, end: datetime, pyrometer_ids: Sequence[str]) -> int:
        where, params = self._filter(start, end, pyrometer_ids)
        statement = text(f"SELECT count(*) FROM public.receiver_data WHERE {where}")
        with self._engine.connect() as connection:
            return int(connection.execute(statement, params).scalar_one())

    def find_series(
        self, start: datetime, end: datetime, pyrometer_ids: Sequence[str]
    ) -> list[ReadingDto]:
        where, params = self._filter(start, end, pyrometer_ids)
        statement = text(
            f"SELECT {COLUMNS} FROM public.receiver_data WHERE {where} "
            "ORDER BY dev_id, reg_date ASC, id ASC"
        )
        return [self._to_reading(row) for row in self._fetch(statement, params)]

    def find_pyrometers(self) -> list[PyrometerDto]:
        statement = text(
            "SELECT DISTINCT ON (dev_id) dev_id, dev_name FROM public.receiver_data "
            "WHERE dev_id IS NOT NULL ORDER BY dev_id, reg_date DESC, id DESC"
        )
        return [PyrometerDto(row["dev_id"], row["dev_name"]) for row in self._fetch(statement, {})]

    def _fetch(
        self, statement: TextClause, params: Mapping[str, Any]
    ) -> Sequence[Mapping[str, Any]]:
        with self._engine.connect() as connection:
            return [dict(row) for row in connection.execute(statement, params).mappings().all()]

    def find_summaries(self) -> list[ReadingDto]:
        statement = text(
            f"SELECT DISTINCT ON (dev_id) {COLUMNS} FROM public.receiver_data "
            "WHERE dev_id IS NOT NULL AND reg_date IS NOT NULL AND reg_temperature IS NOT NULL "
            "ORDER BY dev_id, reg_date DESC, id DESC"
        )
        return [self._to_reading(row) for row in self._fetch(statement, {})]

    def pyrometer_exists(self, pyrometer_id: str) -> bool:
        statement = text("SELECT EXISTS (SELECT 1 FROM public.receiver_data WHERE dev_id = :id)")
        with self._engine.connect() as connection:
            return bool(connection.execute(statement, {"id": pyrometer_id}).scalar_one())

    @staticmethod
    def _filter(
        start: datetime, end: datetime, pyrometer_ids: Sequence[str]
    ) -> tuple[str, dict[str, Any]]:
        params: dict[str, Any] = {"start": start, "end": end}
        if not pyrometer_ids:
            return PERIOD_FILTER, params
        params["ids"] = list(pyrometer_ids)
        return PERIOD_FILTER + PYROMETER_FILTER, params

    @staticmethod
    def _to_reading(row: Mapping[str, Any]) -> ReadingDto:
        gateway_name = row["gtw_name"]
        return ReadingDto(
            id=row["id"],
            gateway_id=row["gtw_id"],
            gateway_name=gateway_name.strip() if gateway_name is not None else None,
            pyrometer_id=row["dev_id"],
            pyrometer_name=row["dev_name"],
            measured_at=row["reg_date"],
            thermocouple=row["reg_thermocouple"],
            unit=row["reg_unit"],
            cold_junction=row["reg_tcj"],
            read_delay=row["reg_read_delay"],
            place=row["reg_place"],
            battery=row["reg_battery"],
            temperature=row["reg_temperature"],
            detect_time=row["reg_detect_time"],
        )

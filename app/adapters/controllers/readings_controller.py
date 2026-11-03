from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, NaiveDatetime

from core.domain.constants.reading_constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from core.domain.errors.period_too_long_error import PeriodTooLongError
from interfaces.core.application.i_get_readings_series_use_case import IGetReadingsSeriesUseCase
from interfaces.core.application.i_list_readings_use_case import IListReadingsUseCase

Start = Annotated[NaiveDatetime, Query(description="Inicio do periodo, horario local sem fuso")]
End = Annotated[NaiveDatetime, Query(description="Fim do periodo, horario local sem fuso")]
PyrometerIds = Annotated[list[str] | None, Query(description="Serial do pirometro (repetivel)")]


class ReadingResponse(BaseModel):
    id: int
    gateway_id: str | None
    gateway_name: str | None
    pyrometer_id: str | None
    pyrometer_name: str | None
    measured_at: datetime | None
    thermocouple: str | None
    unit: str | None
    cold_junction: float | None
    read_delay: int | None
    place: int | None
    battery: int | None
    temperature: int | None
    detect_time: float | None


class ReadingsPageResponse(BaseModel):
    items: list[ReadingResponse]
    total: int
    page: int
    page_size: int


class SeriesPointResponse(BaseModel):
    id: int
    measured_at: datetime | None
    temperature: int | None
    place: int | None


class PyrometerSeriesResponse(BaseModel):
    pyrometer_id: str | None
    pyrometer_name: str | None
    points: list[SeriesPointResponse]


class ReadingsController:
    """GET /readings e GET /readings/series: sempre por periodo, datas sem fuso."""

    def __init__(
        self,
        list_readings_use_case: IListReadingsUseCase,
        get_readings_series_use_case: IGetReadingsSeriesUseCase,
    ) -> None:
        self._list_readings_use_case = list_readings_use_case
        self._get_readings_series_use_case = get_readings_series_use_case
        self.router = APIRouter(tags=["leituras"])
        self.router.add_api_route(
            "/readings",
            self.list_readings,
            methods=["GET"],
            response_model=ReadingsPageResponse,
            summary="Leituras do periodo, da mais recente para a mais antiga",
        )
        self.router.add_api_route(
            "/readings/series",
            self.get_series,
            methods=["GET"],
            response_model=list[PyrometerSeriesResponse],
            summary="Serie de temperaturas por pirometro no periodo (maximo 31 dias)",
        )

    def list_readings(
        self,
        start: Start,
        end: End,
        dev_id: PyrometerIds = None,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    ) -> ReadingsPageResponse:
        result = self._list_readings_use_case.execute(
            start, end, dev_id or [], page=page, page_size=page_size
        )
        return ReadingsPageResponse(
            items=[ReadingResponse.model_validate(asdict(item)) for item in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        )

    def get_series(
        self, start: Start, end: End, dev_id: PyrometerIds = None
    ) -> list[PyrometerSeriesResponse]:
        try:
            series = self._get_readings_series_use_case.execute(start, end, dev_id or [])
        except PeriodTooLongError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return [
            PyrometerSeriesResponse(
                pyrometer_id=item.pyrometer_id,
                pyrometer_name=item.pyrometer_name,
                points=[
                    SeriesPointResponse(
                        id=point.id,
                        measured_at=point.measured_at,
                        temperature=point.temperature,
                        place=point.place,
                    )
                    for point in item.points
                ],
            )
            for item in series
        ]

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from itertools import groupby

from core.domain.constants.reading_constants import MAX_SERIES_PERIOD
from core.domain.dtos.pyrometer_series_dto import PyrometerSeriesDto
from core.domain.errors.period_too_long_error import PeriodTooLongError
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository


class GetReadingsSeriesUseCase:
    def __init__(self, reading_repository: IReadingRepository) -> None:
        self._reading_repository = reading_repository

    def execute(
        self, start: datetime, end: datetime, pyrometer_ids: Sequence[str]
    ) -> list[PyrometerSeriesDto]:
        if end - start > MAX_SERIES_PERIOD:
            raise PeriodTooLongError(MAX_SERIES_PERIOD.days)
        readings = self._reading_repository.find_series(start, end, pyrometer_ids)
        series = []
        for pyrometer_id, group in groupby(readings, key=lambda reading: reading.pyrometer_id):
            points = tuple(group)
            series.append(PyrometerSeriesDto(pyrometer_id, points[-1].pyrometer_name, points))
        return series

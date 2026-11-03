from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from core.domain.dtos.readings_page_dto import ReadingsPageDto
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository


class ListReadingsUseCase:
    def __init__(self, reading_repository: IReadingRepository) -> None:
        self._reading_repository = reading_repository

    def execute(
        self,
        start: datetime,
        end: datetime,
        pyrometer_ids: Sequence[str],
        page: int,
        page_size: int,
    ) -> ReadingsPageDto:
        items = self._reading_repository.find_readings(
            start, end, pyrometer_ids, limit=page_size, offset=(page - 1) * page_size
        )
        total = self._reading_repository.count_readings(start, end, pyrometer_ids)
        return ReadingsPageDto(items=tuple(items), total=total, page=page, page_size=page_size)

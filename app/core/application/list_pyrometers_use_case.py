from __future__ import annotations

from core.domain.dtos.pyrometer_dto import PyrometerDto
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository


class ListPyrometersUseCase:
    def __init__(self, reading_repository: IReadingRepository) -> None:
        self._reading_repository = reading_repository

    def execute(self) -> list[PyrometerDto]:
        return self._reading_repository.find_pyrometers()

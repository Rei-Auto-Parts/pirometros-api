from __future__ import annotations

from core.domain.dtos.pyrometer_overview_dto import PyrometerOverviewDto
from core.domain.models.pyrometer_overview_model import build_overviews
from interfaces.adapters.repositories.i_pyrometer_profile_repository import (
    IPyrometerProfileRepository,
)
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository


class ListPyrometersUseCase:
    """Une os pirometros que existem nos dados com o complemento gravado pela API."""

    def __init__(
        self,
        reading_repository: IReadingRepository,
        profile_repository: IPyrometerProfileRepository,
    ) -> None:
        self._reading_repository = reading_repository
        self._profile_repository = profile_repository

    def execute(self) -> list[PyrometerOverviewDto]:
        return build_overviews(
            self._reading_repository.find_pyrometers(), self._profile_repository.find_all()
        )

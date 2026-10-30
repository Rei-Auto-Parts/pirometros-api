from __future__ import annotations

from core.domain.dtos.health_status_dto import HealthStatusDto
from interfaces.adapters.repositories.i_database_health_repository import (
    IDatabaseHealthRepository,
)


class CheckHealthUseCase:
    def __init__(self, database_health_repository: IDatabaseHealthRepository) -> None:
        self._database_health_repository = database_health_repository

    def execute(self) -> HealthStatusDto:
        return HealthStatusDto(
            api_up=True,
            database_up=self._database_health_repository.is_available(),
        )

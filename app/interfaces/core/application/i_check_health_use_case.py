from __future__ import annotations

from typing import Protocol

from core.domain.dtos.health_status_dto import HealthStatusDto


class ICheckHealthUseCase(Protocol):
    def execute(self) -> HealthStatusDto:
        """Devolve o estado da API e do banco de dados."""
        ...

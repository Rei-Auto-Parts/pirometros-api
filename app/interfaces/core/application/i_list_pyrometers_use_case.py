from __future__ import annotations

from typing import Protocol

from core.domain.dtos.pyrometer_overview_dto import PyrometerOverviewDto


class IListPyrometersUseCase(Protocol):
    def execute(self) -> list[PyrometerOverviewDto]:
        """Pirometros existentes com o complemento e os padroes aplicados, por serial."""
        ...

from __future__ import annotations

from typing import Protocol

from core.domain.dtos.pyrometer_summary_dto import PyrometerSummaryDto


class IListPyrometerSummariesUseCase(Protocol):
    def execute(self) -> list[PyrometerSummaryDto]:
        """A leitura mais recente com temperatura de cada pirometro, e ha quantos minutos."""
        ...

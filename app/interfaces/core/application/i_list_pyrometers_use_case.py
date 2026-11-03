from __future__ import annotations

from typing import Protocol

from core.domain.dtos.pyrometer_dto import PyrometerDto


class IListPyrometersUseCase(Protocol):
    def execute(self) -> list[PyrometerDto]:
        """Pirometros existentes, com serial e nome atual."""
        ...

from __future__ import annotations

from typing import Protocol

from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto


class IPyrometerProfileRepository(Protocol):
    """Complemento dos pirometros, guardado pela propria API no schema `app`."""

    def find_all(self) -> list[PyrometerProfileDto]:
        """Todos os complementos gravados."""
        ...

    def save(self, profile: PyrometerProfileDto) -> None:
        """Grava o complemento: o primeiro cria, os seguintes substituem."""
        ...

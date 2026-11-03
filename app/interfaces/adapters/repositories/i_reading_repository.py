from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.reading_dto import ReadingDto


class IReadingRepository(Protocol):
    """Leitura das medicoes gravadas pelo sincronizador. Nunca escreve."""

    def find_readings(
        self,
        start: datetime,
        end: datetime,
        pyrometer_ids: Sequence[str],
        limit: int,
        offset: int,
    ) -> list[ReadingDto]:
        """Medicoes de `start` a `end` (inclusivos), da mais recente para a mais antiga.

        `pyrometer_ids` vazio significa todos os pirometros.
        """
        ...

    def count_readings(self, start: datetime, end: datetime, pyrometer_ids: Sequence[str]) -> int:
        """Quantas medicoes existem no periodo, com o mesmo filtro de `find_readings`."""
        ...

    def find_series(
        self, start: datetime, end: datetime, pyrometer_ids: Sequence[str]
    ) -> list[ReadingDto]:
        """Todas as medicoes do periodo, por pirometro e da mais antiga para a mais recente."""
        ...

    def find_pyrometers(self) -> list[PyrometerDto]:
        """Um item por pirometro, com o nome da medicao mais recente."""
        ...

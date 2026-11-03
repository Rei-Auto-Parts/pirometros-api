from __future__ import annotations

from dataclasses import dataclass

from core.domain.dtos.reading_dto import ReadingDto


@dataclass(frozen=True)
class PyrometerSeriesDto:
    """Medicoes de um pirometro, da mais antiga para a mais recente."""

    pyrometer_id: str | None
    pyrometer_name: str | None
    points: tuple[ReadingDto, ...]

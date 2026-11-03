from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from core.domain.dtos.pyrometer_series_dto import PyrometerSeriesDto


class IGetReadingsSeriesUseCase(Protocol):
    def execute(
        self, start: datetime, end: datetime, pyrometer_ids: Sequence[str]
    ) -> list[PyrometerSeriesDto]:
        """Serie por pirometro. Levanta `PeriodTooLongError` se o periodo passar de 31 dias."""
        ...

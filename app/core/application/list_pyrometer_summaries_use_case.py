from __future__ import annotations

from core.domain.dtos.pyrometer_summary_dto import PyrometerSummaryDto
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository
from interfaces.infra.tools.i_clock_tool import IClockTool

SECONDS_PER_MINUTE = 60


class ListPyrometerSummariesUseCase:
    def __init__(self, reading_repository: IReadingRepository, clock: IClockTool) -> None:
        self._reading_repository = reading_repository
        self._clock = clock

    def execute(self) -> list[PyrometerSummaryDto]:
        readings = self._reading_repository.find_summaries()
        now = self._clock.now()
        summaries: list[PyrometerSummaryDto] = []
        for reading in readings:
            if (
                reading.pyrometer_id is None
                or reading.measured_at is None
                or reading.temperature is None
            ):
                continue
            elapsed = (now - reading.measured_at).total_seconds()
            summaries.append(
                PyrometerSummaryDto(
                    pyrometer_id=reading.pyrometer_id,
                    temperature=reading.temperature,
                    measured_at=reading.measured_at,
                    battery=reading.battery,
                    minutes_without_reading=max(0, int(elapsed // SECONDS_PER_MINUTE)),
                )
            )
        return summaries

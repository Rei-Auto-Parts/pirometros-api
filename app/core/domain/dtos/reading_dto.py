from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReadingDto:
    """Uma medicao como esta gravada. `measured_at` e horario local, sem fuso."""

    id: int
    gateway_id: str | None
    gateway_name: str | None
    pyrometer_id: str | None
    pyrometer_name: str | None
    measured_at: datetime | None
    thermocouple: str | None
    unit: str | None
    cold_junction: float | None
    read_delay: int | None
    place: int | None
    battery: int | None
    temperature: int | None
    detect_time: float | None

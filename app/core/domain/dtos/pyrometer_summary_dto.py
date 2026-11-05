from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PyrometerSummaryDto:
    """Ultima leitura com temperatura de um pirometro. `measured_at` e horario local, sem fuso."""

    pyrometer_id: str
    temperature: int
    measured_at: datetime
    battery: int | None
    minutes_without_reading: int

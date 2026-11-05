from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


class ClockTool:
    """O agora em horario local, sem fuso. O fuso serve so para isto: nunca converte `reg_date`."""

    def __init__(self, timezone: str) -> None:
        self._zone = ZoneInfo(timezone)

    def now(self) -> datetime:
        return datetime.now(self._zone).replace(tzinfo=None)

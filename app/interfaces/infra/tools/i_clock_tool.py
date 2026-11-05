from __future__ import annotations

from datetime import datetime
from typing import Protocol


class IClockTool(Protocol):
    def now(self) -> datetime:
        """O agora em horario local, sem fuso (naive)."""
        ...

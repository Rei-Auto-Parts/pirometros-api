from __future__ import annotations

from datetime import datetime


class FixedClock:
    """Relogio dos testes: o \"agora\" e o que o teste mandar."""

    def __init__(self, current: datetime) -> None:
        self.current = current

    def now(self) -> datetime:
        return self.current

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PyrometerDto:
    id: str
    name: str | None

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PyrometerProfileDto:
    """O complemento gravado de um pirometro existente. Campo `None` = nao informado."""

    pyrometer_id: str
    nickname: str | None
    color: str | None
    note: str | None
    active: bool

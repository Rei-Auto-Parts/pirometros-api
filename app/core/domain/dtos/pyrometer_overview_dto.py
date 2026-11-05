from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PyrometerOverviewDto:
    """Pirometro existente com o complemento e os padroes ja aplicados. `color` nunca e nula."""

    id: str
    name: str | None
    nickname: str | None
    color: str
    note: str | None
    active: bool

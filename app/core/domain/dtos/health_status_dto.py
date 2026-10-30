from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatusDto:
    """Resultado da checagem de saude: a API sempre responde; o banco pode estar fora."""

    api_up: bool
    database_up: bool

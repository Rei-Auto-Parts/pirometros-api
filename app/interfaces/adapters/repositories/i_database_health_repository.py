from __future__ import annotations

from typing import Protocol


class IDatabaseHealthRepository(Protocol):
    """Sonda de disponibilidade do banco `pirometros`."""

    def is_available(self) -> bool:
        """True quando o banco aceita conexao e responde a uma consulta trivial."""
        ...

from __future__ import annotations


class ColorInUseError(Exception):
    """A cor ja pertence a outro pirometro (escolhida ou padrao)."""

    def __init__(self, color: str) -> None:
        super().__init__(f"a cor '{color}' ja esta em uso por outro pirometro")
        self.color = color

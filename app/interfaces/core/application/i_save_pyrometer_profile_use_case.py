from __future__ import annotations

from typing import Protocol


class ISavePyrometerProfileUseCase(Protocol):
    def execute(
        self,
        pyrometer_id: str,
        nickname: str | None,
        color: str | None,
        note: str | None,
        active: bool,
    ) -> None:
        """Grava o complemento de um pirometro existente.

        Levanta `PyrometerNotFoundError` se o serial nao existe nos dados.
        """
        ...

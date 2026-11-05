from __future__ import annotations


class PyrometerNotFoundError(Exception):
    """O serial informado nao existe nos dados gravados pelo sincronizador."""

    def __init__(self, pyrometer_id: str) -> None:
        super().__init__(f"pirometro '{pyrometer_id}' nao encontrado")
        self.pyrometer_id = pyrometer_id

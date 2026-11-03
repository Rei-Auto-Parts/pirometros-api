from __future__ import annotations


class PeriodTooLongError(Exception):
    """O periodo pedido passa do maximo permitido para a consulta."""

    def __init__(self, max_days: int) -> None:
        super().__init__(f"o periodo maximo e de {max_days} dias")
        self.max_days = max_days

from __future__ import annotations

from logging import Logger

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseHealthRepository:
    def __init__(self, engine: Engine, logger: Logger) -> None:
        self._engine = engine
        self._logger = logger

    def is_available(self) -> bool:
        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as error:
            # Registra so o tipo do erro: a mensagem do driver pode carregar o DSN.
            self._logger.warning("database unavailable: %s", type(error).__name__)
            return False
        return True

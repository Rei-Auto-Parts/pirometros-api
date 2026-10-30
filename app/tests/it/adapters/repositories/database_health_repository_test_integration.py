import logging
import os

from adapters.repositories.database_health_repository import DatabaseHealthRepository
from infra.tools.database_tool import build_engine

LOGGER = logging.getLogger("it")


def test_should_return_true_when_postgres_is_reachable() -> None:
    # Arrange
    repository = DatabaseHealthRepository(build_engine(os.environ["DATABASE_URL"]), LOGGER)

    # Act
    result = repository.is_available()

    # Assert
    assert result is True


def test_should_return_false_when_postgres_is_unreachable() -> None:
    # Arrange
    engine = build_engine("postgresql+psycopg://x:x@127.0.0.1:1/x")
    repository = DatabaseHealthRepository(engine, LOGGER)

    # Act
    result = repository.is_available()

    # Assert
    assert result is False

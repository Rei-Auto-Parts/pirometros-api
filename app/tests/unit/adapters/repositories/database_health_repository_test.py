from logging import Logger

from pytest_mock import MockerFixture
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from adapters.repositories.database_health_repository import DatabaseHealthRepository


def test_should_return_true_when_query_succeeds(mocker: MockerFixture) -> None:
    # Arrange
    engine = mocker.MagicMock(spec=Engine)
    logger = mocker.Mock(spec=Logger)
    repository = DatabaseHealthRepository(engine, logger)

    # Act
    result = repository.is_available()

    # Assert
    assert result is True
    engine.connect.assert_called_once_with()
    logger.warning.assert_not_called()


def test_should_return_false_when_connection_fails(mocker: MockerFixture) -> None:
    # Arrange
    engine = mocker.MagicMock(spec=Engine)
    engine.connect.side_effect = OperationalError("SELECT 1", {}, Exception("boom"))
    logger = mocker.Mock(spec=Logger)
    repository = DatabaseHealthRepository(engine, logger)

    # Act
    result = repository.is_available()

    # Assert
    assert result is False


def test_should_log_only_error_type_when_connection_fails(mocker: MockerFixture) -> None:
    # Arrange
    engine = mocker.MagicMock(spec=Engine)
    engine.connect.side_effect = OperationalError("SELECT 1", {}, Exception("senha=secreta"))
    logger = mocker.Mock(spec=Logger)
    repository = DatabaseHealthRepository(engine, logger)

    # Act
    repository.is_available()

    # Assert
    logger.warning.assert_called_once_with("database unavailable: %s", "OperationalError")

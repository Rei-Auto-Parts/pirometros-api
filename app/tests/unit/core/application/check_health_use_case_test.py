import pytest
from pytest_mock import MockerFixture

from core.application.check_health_use_case import CheckHealthUseCase
from core.domain.dtos.health_status_dto import HealthStatusDto
from interfaces.adapters.repositories.i_database_health_repository import (
    IDatabaseHealthRepository,
)


@pytest.mark.parametrize("database_up", [True, False])
def test_should_report_database_state_when_repository_answers(
    mocker: MockerFixture, database_up: bool
) -> None:
    # Arrange
    repository = mocker.Mock(spec=IDatabaseHealthRepository)
    repository.is_available.return_value = database_up
    use_case = CheckHealthUseCase(repository)

    # Act
    result = use_case.execute()

    # Assert
    assert result == HealthStatusDto(api_up=True, database_up=database_up)


def test_should_probe_database_once_when_executed(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IDatabaseHealthRepository)
    use_case = CheckHealthUseCase(repository)

    # Act
    use_case.execute()

    # Assert
    repository.is_available.assert_called_once_with()

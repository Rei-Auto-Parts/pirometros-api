from pytest_mock import MockerFixture

from core.application.list_pyrometers_use_case import ListPyrometersUseCase
from core.domain.dtos.pyrometer_dto import PyrometerDto
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository


def test_should_return_pyrometers_when_repository_answers(mocker: MockerFixture) -> None:
    # Arrange
    pyrometers = [PyrometerDto("C24C.F90D.0000", "PI-12"), PyrometerDto("B68A.1010.0000", "PI-14")]
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_pyrometers.return_value = pyrometers
    use_case = ListPyrometersUseCase(repository)

    # Act
    result = use_case.execute()

    # Assert
    assert result == pyrometers


def test_should_query_repository_once_when_executed(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_pyrometers.return_value = []
    use_case = ListPyrometersUseCase(repository)

    # Act
    use_case.execute()

    # Assert
    repository.find_pyrometers.assert_called_once_with()

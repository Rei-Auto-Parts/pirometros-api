from datetime import datetime

from pytest_mock import MockerFixture

from core.application.list_readings_use_case import ListReadingsUseCase
from core.domain.dtos.reading_dto import ReadingDto
from core.domain.dtos.readings_page_dto import ReadingsPageDto
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository

START = datetime(2026, 10, 29, 0, 0, 0)
END = datetime(2026, 10, 29, 23, 59, 59)


def build_reading(reading_id: int) -> ReadingDto:
    return ReadingDto(
        id=reading_id,
        gateway_id="B571.430C.0000",
        gateway_name="RERF",
        pyrometer_id="C24C.F90D.0000",
        pyrometer_name="PI-12",
        measured_at=datetime(2026, 10, 29, 11, 0, 30),
        thermocouple="S",
        unit="Celsius",
        cold_junction=31.4,
        read_delay=0,
        place=60,
        battery=61,
        temperature=1610,
        detect_time=3.9,
    )


def test_should_return_page_with_items_and_total_when_repository_answers(
    mocker: MockerFixture,
) -> None:
    # Arrange
    readings = [build_reading(2), build_reading(1)]
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_readings.return_value = readings
    repository.count_readings.return_value = 120
    use_case = ListReadingsUseCase(repository)

    # Act
    result = use_case.execute(START, END, [], page=1, page_size=50)

    # Assert
    assert result == ReadingsPageDto(items=tuple(readings), total=120, page=1, page_size=50)


def test_should_skip_previous_pages_when_page_is_greater_than_one(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_readings.return_value = []
    repository.count_readings.return_value = 0
    use_case = ListReadingsUseCase(repository)

    # Act
    use_case.execute(START, END, ["C24C.F90D.0000"], page=3, page_size=50)

    # Assert
    repository.find_readings.assert_called_once_with(
        START, END, ["C24C.F90D.0000"], limit=50, offset=100
    )


def test_should_count_with_same_filter_when_listing(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_readings.return_value = []
    repository.count_readings.return_value = 0
    use_case = ListReadingsUseCase(repository)

    # Act
    use_case.execute(START, END, ["C24C.F90D.0000"], page=1, page_size=50)

    # Assert
    repository.count_readings.assert_called_once_with(START, END, ["C24C.F90D.0000"])

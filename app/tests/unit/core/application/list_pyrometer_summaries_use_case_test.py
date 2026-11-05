from datetime import datetime
from unittest.mock import Mock

from pytest_mock import MockerFixture

from core.application.list_pyrometer_summaries_use_case import ListPyrometerSummariesUseCase
from core.domain.dtos.pyrometer_summary_dto import PyrometerSummaryDto
from core.domain.dtos.reading_dto import ReadingDto
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository
from interfaces.infra.tools.i_clock_tool import IClockTool

PI12 = "C24C.F90D.0000"


def build_reading(**overrides: object) -> ReadingDto:
    values: dict[str, object] = {
        "id": 1,
        "gateway_id": None,
        "gateway_name": None,
        "pyrometer_id": PI12,
        "pyrometer_name": "PI-12",
        "measured_at": datetime(2026, 11, 5, 10, 5, 0),
        "thermocouple": "S",
        "unit": "Celsius",
        "cold_junction": None,
        "read_delay": 0,
        "place": 60,
        "battery": 62,
        "temperature": 1510,
        "detect_time": None,
    }
    values.update(overrides)
    return ReadingDto(**values)  # type: ignore[arg-type]


def build_use_case(
    mocker: MockerFixture, readings: list[ReadingDto], now: datetime
) -> tuple[ListPyrometerSummariesUseCase, Mock, Mock]:
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_summaries.return_value = readings
    clock = mocker.Mock(spec=IClockTool)
    clock.now.return_value = now
    return ListPyrometerSummariesUseCase(repository, clock), repository, clock


def test_should_return_minutes_since_last_reading_when_summarizing(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, _ = build_use_case(mocker, [build_reading()], datetime(2026, 11, 5, 10, 8, 30))

    # Act
    result = use_case.execute()

    # Assert
    assert result == [
        PyrometerSummaryDto(PI12, 1510, datetime(2026, 11, 5, 10, 5, 0), 62, 3),
    ]


def test_should_floor_the_minutes_when_seconds_are_left(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, _ = build_use_case(mocker, [build_reading()], datetime(2026, 11, 5, 10, 5, 59))

    # Act
    result = use_case.execute()

    # Assert
    assert result[0].minutes_without_reading == 0


def test_should_never_return_negative_minutes_when_reading_is_in_the_future(
    mocker: MockerFixture,
) -> None:
    # Arrange
    use_case, _, _ = build_use_case(mocker, [build_reading()], datetime(2026, 11, 5, 10, 0, 0))

    # Act
    result = use_case.execute()

    # Assert
    assert result[0].minutes_without_reading == 0


def test_should_skip_readings_without_date_or_temperature_or_serial(mocker: MockerFixture) -> None:
    # Arrange
    readings = [
        build_reading(measured_at=None),
        build_reading(temperature=None),
        build_reading(pyrometer_id=None),
    ]
    use_case, _, _ = build_use_case(mocker, readings, datetime(2026, 11, 5, 10, 8, 0))

    # Act
    result = use_case.execute()

    # Assert
    assert result == []


def test_should_return_nothing_when_there_are_no_readings(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, _ = build_use_case(mocker, [], datetime(2026, 11, 5, 10, 8, 0))

    # Act
    result = use_case.execute()

    # Assert
    assert result == []


def test_should_read_repository_and_clock_once_when_executed(mocker: MockerFixture) -> None:
    # Arrange
    use_case, repository, clock = build_use_case(
        mocker, [build_reading()], datetime(2026, 11, 5, 10, 8, 0)
    )

    # Act
    use_case.execute()

    # Assert
    repository.find_summaries.assert_called_once_with()
    clock.now.assert_called_once_with()

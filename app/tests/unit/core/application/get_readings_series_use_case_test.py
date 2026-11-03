from datetime import datetime, timedelta

import pytest
from pytest_mock import MockerFixture

from core.application.get_readings_series_use_case import GetReadingsSeriesUseCase
from core.domain.dtos.pyrometer_series_dto import PyrometerSeriesDto
from core.domain.dtos.reading_dto import ReadingDto
from core.domain.errors.period_too_long_error import PeriodTooLongError
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository

START = datetime(2026, 10, 1, 0, 0, 0)


def build_reading(reading_id: int, pyrometer_id: str, pyrometer_name: str) -> ReadingDto:
    return ReadingDto(
        id=reading_id,
        gateway_id=None,
        gateway_name=None,
        pyrometer_id=pyrometer_id,
        pyrometer_name=pyrometer_name,
        measured_at=datetime(2026, 10, 1, 8, reading_id, 0),
        thermocouple="S",
        unit="Celsius",
        cold_junction=None,
        read_delay=0,
        place=60,
        battery=61,
        temperature=1500 + reading_id,
        detect_time=None,
    )


def test_should_group_points_by_pyrometer_when_repository_returns_readings(
    mocker: MockerFixture,
) -> None:
    # Arrange
    pi12_a, pi12_b = build_reading(1, "A", "PI-12"), build_reading(2, "A", "PI-12")
    pi14 = build_reading(3, "B", "PI-14")
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_series.return_value = [pi12_a, pi12_b, pi14]
    use_case = GetReadingsSeriesUseCase(repository)

    # Act
    result = use_case.execute(START, START + timedelta(days=1), [])

    # Assert
    assert result == [
        PyrometerSeriesDto("A", "PI-12", (pi12_a, pi12_b)),
        PyrometerSeriesDto("B", "PI-14", (pi14,)),
    ]


def test_should_return_empty_list_when_there_are_no_readings(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_series.return_value = []
    use_case = GetReadingsSeriesUseCase(repository)

    # Act
    result = use_case.execute(START, START + timedelta(days=1), [])

    # Assert
    assert result == []


def test_should_query_repository_with_given_filter_when_period_is_valid(
    mocker: MockerFixture,
) -> None:
    # Arrange
    end = START + timedelta(days=1)
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_series.return_value = []
    use_case = GetReadingsSeriesUseCase(repository)

    # Act
    use_case.execute(START, end, ["A"])

    # Assert
    repository.find_series.assert_called_once_with(START, end, ["A"])


def test_should_accept_period_of_exactly_31_days(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    repository.find_series.return_value = []
    use_case = GetReadingsSeriesUseCase(repository)

    # Act
    use_case.execute(START, START + timedelta(days=31), [])

    # Assert
    repository.find_series.assert_called_once()


def test_should_raise_period_too_long_when_period_exceeds_31_days(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    use_case = GetReadingsSeriesUseCase(repository)

    # Act
    with pytest.raises(PeriodTooLongError) as error:
        use_case.execute(START, START + timedelta(days=40), [])

    # Assert
    assert error.value.max_days == 31


def test_should_not_query_repository_when_period_exceeds_31_days(mocker: MockerFixture) -> None:
    # Arrange
    repository = mocker.Mock(spec=IReadingRepository)
    use_case = GetReadingsSeriesUseCase(repository)

    # Act
    with pytest.raises(PeriodTooLongError):
        use_case.execute(START, START + timedelta(days=40), [])

    # Assert
    repository.find_series.assert_not_called()

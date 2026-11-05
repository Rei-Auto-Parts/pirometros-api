from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Engine

from adapters.repositories.reading_repository import ReadingRepository
from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.reading_dto import ReadingDto

START = datetime(2026, 10, 29, 0, 0, 0)
END = datetime(2026, 10, 29, 23, 59, 59)


def build_row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": 94,
        "gtw_id": "B571.430C.0000",
        "gtw_name": "RERF ",
        "dev_id": "C24C.F90D.0000",
        "dev_name": "PI-12",
        "reg_date": datetime(2026, 10, 29, 11, 0, 30),
        "reg_thermocouple": "S",
        "reg_unit": "Celsius",
        "reg_tcj": 31.4,
        "reg_read_delay": 0,
        "reg_place": 60,
        "reg_battery": 63,
        "reg_temperature": 1548,
        "reg_detect_time": 3.9,
    }
    row.update(overrides)
    return row


def build_repository(mocker: MockerFixture, rows: list[dict[str, Any]]) -> tuple[Any, Any]:
    engine = mocker.MagicMock(spec=Engine)
    connection = engine.connect.return_value.__enter__.return_value
    connection.execute.return_value.mappings.return_value.all.return_value = rows
    return ReadingRepository(engine), connection


def test_should_map_row_to_reading_when_finding_readings(mocker: MockerFixture) -> None:
    # Arrange
    repository, _ = build_repository(mocker, [build_row()])

    # Act
    result = repository.find_readings(START, END, [], limit=50, offset=0)

    # Assert
    assert result == [
        ReadingDto(
            id=94,
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
            battery=63,
            temperature=1548,
            detect_time=3.9,
        )
    ]


def test_should_keep_gateway_name_none_when_row_has_no_gateway_name(mocker: MockerFixture) -> None:
    # Arrange
    repository, _ = build_repository(mocker, [build_row(gtw_name=None)])

    # Act
    result = repository.find_readings(START, END, [], limit=50, offset=0)

    # Assert
    assert result[0].gateway_name is None


def test_should_bind_period_and_page_when_no_pyrometer_is_given(mocker: MockerFixture) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])

    # Act
    repository.find_readings(START, END, [], limit=50, offset=100)

    # Assert
    connection.execute.assert_called_once()
    assert connection.execute.call_args.args[1] == {
        "start": START,
        "end": END,
        "limit": 50,
        "offset": 100,
    }


def test_should_filter_by_pyrometer_when_ids_are_given(mocker: MockerFixture) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])

    # Act
    repository.find_readings(START, END, ["C24C.F90D.0000"], limit=50, offset=0)

    # Assert
    statement, params = connection.execute.call_args.args
    assert "dev_id = ANY(:ids)" in str(statement)
    assert params["ids"] == ["C24C.F90D.0000"]


def test_should_not_filter_by_pyrometer_when_no_id_is_given(mocker: MockerFixture) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])

    # Act
    repository.find_readings(START, END, [], limit=50, offset=0)

    # Assert
    assert (
        "dev_id"
        not in str(connection.execute.call_args.args[0]).split("WHERE")[1].split("ORDER")[0]
    )


def test_should_order_by_date_descending_when_finding_readings(mocker: MockerFixture) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])

    # Act
    repository.find_readings(START, END, [], limit=50, offset=0)

    # Assert
    assert "ORDER BY reg_date DESC, id DESC" in str(connection.execute.call_args.args[0])


def test_should_return_total_when_counting_readings(mocker: MockerFixture) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])
    connection.execute.return_value.scalar_one.return_value = 120

    # Act
    result = repository.count_readings(START, END, [])

    # Assert
    assert result == 120


def test_should_order_by_pyrometer_and_date_ascending_when_finding_series(
    mocker: MockerFixture,
) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [build_row()])

    # Act
    result = repository.find_series(START, END, [])

    # Assert
    assert "ORDER BY dev_id, reg_date ASC, id ASC" in str(connection.execute.call_args.args[0])
    assert result[0].id == 94


def test_should_map_rows_to_pyrometers_when_finding_pyrometers(mocker: MockerFixture) -> None:
    # Arrange
    repository, _ = build_repository(
        mocker,
        [
            {"dev_id": "B68A.1010.0000", "dev_name": "PI-14"},
            {"dev_id": "C24C.F90D.0000", "dev_name": "PI-12"},
        ],
    )

    # Act
    result = repository.find_pyrometers()

    # Assert
    assert result == [
        PyrometerDto("B68A.1010.0000", "PI-14"),
        PyrometerDto("C24C.F90D.0000", "PI-12"),
    ]


@pytest.mark.parametrize(
    "call",
    [
        lambda repository: repository.find_readings(START, END, [], limit=1, offset=0),
        lambda repository: repository.count_readings(START, END, []),
        lambda repository: repository.find_series(START, END, []),
    ],
)
def test_should_exclude_readings_without_temperature_when_filtering_by_period(
    mocker: MockerFixture, call: Callable[[Any], Any]
) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])

    # Act
    call(repository)

    # Assert
    assert "reg_temperature IS NOT NULL" in str(connection.execute.call_args.args[0])


def test_should_return_latest_reading_with_temperature_when_finding_summaries(
    mocker: MockerFixture,
) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [build_row()])

    # Act
    result = repository.find_summaries()

    # Assert
    statement = str(connection.execute.call_args.args[0])
    assert "DISTINCT ON (dev_id)" in statement
    assert "reg_temperature IS NOT NULL" in statement
    assert "ORDER BY dev_id, reg_date DESC, id DESC" in statement
    assert result[0].temperature == 1548


@pytest.mark.parametrize("found", [True, False])
def test_should_return_whether_serial_exists_when_checking_pyrometer(
    mocker: MockerFixture, found: bool
) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])
    connection.execute.return_value.scalar_one.return_value = found

    # Act
    result = repository.pyrometer_exists("C24C.F90D.0000")

    # Assert
    assert result is found
    assert connection.execute.call_args.args[1] == {"id": "C24C.F90D.0000"}


@pytest.mark.parametrize(
    "call",
    [
        lambda repository: repository.find_readings(START, END, [], limit=1, offset=0),
        lambda repository: repository.count_readings(START, END, []),
        lambda repository: repository.find_series(START, END, []),
        lambda repository: repository.find_pyrometers(),
        lambda repository: repository.find_summaries(),
        lambda repository: repository.pyrometer_exists("C24C.F90D.0000"),
    ],
)
def test_should_only_select_when_reading_from_receiver_data(
    mocker: MockerFixture, call: Callable[[Any], Any]
) -> None:
    # Arrange
    repository, connection = build_repository(mocker, [])

    # Act
    call(repository)

    # Assert
    assert str(connection.execute.call_args.args[0]).lstrip().upper().startswith("SELECT")

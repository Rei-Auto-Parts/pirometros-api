import time
from datetime import datetime

from sqlalchemy import Engine

from adapters.repositories.reading_repository import ReadingRepository
from core.domain.dtos.pyrometer_dto import PyrometerDto
from tests.support.receiver_data_fixture import (
    insert_generated,
    insert_reading,
    snapshot_readings,
)

DAY_START = datetime(2026, 10, 29, 0, 0, 0)
DAY_END = datetime(2026, 10, 29, 23, 59, 59)
PI_12 = "C24C.F90D.0000"
PI_14 = "B68A.1010.0000"


def test_should_order_by_measurement_date_when_arrival_order_differs(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 14, 2, 0), PI_14, "PI-14")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 9, 0, 0), PI_14, "PI-14")
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_readings(DAY_START, DAY_END, [], limit=50, offset=0)

    # Assert
    assert [reading.id for reading in result] == [1, 2]


def test_should_include_both_period_bounds_when_reading_falls_exactly_on_them(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, DAY_START)
    insert_reading(clean_readings, 2, DAY_END)
    insert_reading(clean_readings, 3, datetime(2026, 10, 30, 0, 0, 0))
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_readings(DAY_START, DAY_END, [], limit=50, offset=0)

    # Assert
    assert [reading.id for reading in result] == [2, 1]


def test_should_return_only_requested_pyrometer_when_filtering_by_id(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 11, 0, 0), PI_14, "PI-14")
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_readings(DAY_START, DAY_END, [PI_12], limit=50, offset=0)

    # Assert
    assert [reading.pyrometer_id for reading in result] == [PI_12]


def test_should_page_results_and_count_total_when_period_has_more_than_one_page(
    clean_readings: Engine,
) -> None:
    # Arrange
    for index in range(5):
        insert_reading(clean_readings, index + 1, datetime(2026, 10, 29, 10, index, 0))
    repository = ReadingRepository(clean_readings)

    # Act
    page = repository.find_readings(DAY_START, DAY_END, [], limit=2, offset=2)
    total = repository.count_readings(DAY_START, DAY_END, [])

    # Assert
    assert [reading.id for reading in page] == [3, 2]
    assert total == 5


def test_should_trim_gateway_name_when_reading_is_stored_with_trailing_space(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), gateway_name="RERF ")
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_readings(DAY_START, DAY_END, [], limit=50, offset=0)

    # Assert
    assert result[0].gateway_name == "RERF"


def test_should_return_stored_date_without_timezone_when_reading(clean_readings: Engine) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 11, 0, 30))
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_readings(DAY_START, DAY_END, [], limit=50, offset=0)

    # Assert
    assert result[0].measured_at == datetime(2026, 10, 29, 11, 0, 30)
    assert result[0].measured_at is not None
    assert result[0].measured_at.tzinfo is None


def test_should_group_series_by_pyrometer_in_ascending_date_when_finding_series(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 11, 0, 0), PI_14, "PI-14")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    insert_reading(clean_readings, 3, datetime(2026, 10, 29, 9, 0, 0), PI_14, "PI-14")
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_series(DAY_START, DAY_END, [])

    # Assert
    assert [(reading.pyrometer_id, reading.id) for reading in result] == [
        (PI_14, 3),
        (PI_14, 1),
        (PI_12, 2),
    ]


def test_should_return_name_of_latest_reading_when_listing_pyrometers(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 28, 10, 0, 0), PI_12, "PI-12")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12B")
    insert_reading(clean_readings, 3, datetime(2026, 10, 29, 11, 0, 0), PI_14, "PI-14")
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_pyrometers()

    # Assert
    assert result == [PyrometerDto(PI_14, "PI-14"), PyrometerDto(PI_12, "PI-12B")]


def test_should_leave_table_untouched_when_every_query_runs(clean_readings: Engine) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0))
    repository = ReadingRepository(clean_readings)
    before = snapshot_readings(clean_readings)

    # Act
    repository.find_readings(DAY_START, DAY_END, [], limit=50, offset=0)
    repository.count_readings(DAY_START, DAY_END, [])
    repository.find_series(DAY_START, DAY_END, [])
    repository.find_pyrometers()

    # Assert
    assert snapshot_readings(clean_readings) == before


def test_should_answer_within_500_ms_when_period_has_10000_readings(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_generated(clean_readings, 10_000, DAY_START)
    repository = ReadingRepository(clean_readings)
    week_start, week_end = datetime(2026, 10, 25, 0, 0, 0), datetime(2026, 10, 31, 23, 59, 59)

    # Act
    started = time.perf_counter()
    page = repository.find_readings(week_start, week_end, [], limit=500, offset=0)
    repository.count_readings(week_start, week_end, [])
    elapsed = time.perf_counter() - started

    # Assert
    assert len(page) == 500
    assert elapsed < 0.5


def test_should_exclude_readings_without_temperature_when_listing_counting_and_serializing(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), temperature=1500)
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 11, 0, 0), temperature=None)
    insert_reading(clean_readings, 3, datetime(2026, 10, 29, 12, 0, 0), temperature=1520)
    repository = ReadingRepository(clean_readings)

    # Act
    listed = repository.find_readings(DAY_START, DAY_END, [], limit=50, offset=0)
    total = repository.count_readings(DAY_START, DAY_END, [])
    series = repository.find_series(DAY_START, DAY_END, [])

    # Assert
    assert [reading.id for reading in listed] == [3, 1]
    assert total == 2
    assert [reading.id for reading in series] == [1, 3]


def test_should_return_the_latest_reading_with_temperature_when_finding_summaries(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12", 1500)
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 10, 5, 0), PI_12, "PI-12", None)
    insert_reading(clean_readings, 3, datetime(2026, 10, 29, 9, 0, 0), PI_14, "PI-14", 1400)
    repository = ReadingRepository(clean_readings)

    # Act
    result = {reading.pyrometer_id: reading for reading in repository.find_summaries()}

    # Assert
    assert result[PI_12].id == 1
    assert result[PI_12].temperature == 1500
    assert result[PI_14].id == 3


def test_should_leave_out_pyrometers_without_any_temperature_when_finding_summaries(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12", None)
    repository = ReadingRepository(clean_readings)

    # Act
    result = repository.find_summaries()

    # Assert
    assert result == []


def test_should_tell_whether_the_serial_exists_when_checking_pyrometer(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    repository = ReadingRepository(clean_readings)

    # Act
    found = repository.pyrometer_exists(PI_12)
    missing = repository.pyrometer_exists("ZZZZ.0000.0000")

    # Assert
    assert (found, missing) == (True, False)

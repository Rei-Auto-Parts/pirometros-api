import time
from datetime import datetime

from sqlalchemy import Engine

from tests.support.api_client import build_api_client
from tests.support.fixed_clock import FixedClock
from tests.support.receiver_data_fixture import (
    insert_many_pyrometers,
    insert_reading,
    snapshot_readings,
)

PI_12 = "C24C.F90D.0000"
PI_14 = "B68A.1010.0000"
DAY = datetime(2026, 10, 29, 0, 0, 0)


def test_should_list_pyrometers_with_defaults_when_no_profile_exists(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    client = build_api_client(clean_readings)

    # Act
    body = client.get("/api/pyrometers").json()

    # Assert
    assert len(body) == 1
    assert (body[0]["id"], body[0]["name"], body[0]["nickname"], body[0]["note"]) == (
        PI_12,
        "PI-12",
        None,
        None,
    )
    assert body[0]["active"] is True
    assert body[0]["color"].startswith("#")


def test_should_serve_the_saved_profile_when_putting_then_listing(clean_readings: Engine) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    client = build_api_client(clean_readings)
    profile = {"nickname": "Forno 2", "color": "#e11d48", "note": "termopar trocado"}

    # Act
    put = client.put(f"/api/pyrometers/{PI_12}", json=profile)
    listed = client.get("/api/pyrometers").json()

    # Assert
    assert put.status_code == 200
    assert listed[0]["nickname"] == "Forno 2"
    assert listed[0]["color"] == "#e11d48"
    assert listed[0]["note"] == "termopar trocado"


def test_should_keep_the_profile_when_the_app_is_recreated(clean_readings: Engine) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    build_api_client(clean_readings).put(f"/api/pyrometers/{PI_12}", json={"nickname": "Forno 2"})

    # Act
    listed = build_api_client(clean_readings).get("/api/pyrometers").json()

    # Assert
    assert listed[0]["nickname"] == "Forno 2"


def test_should_answer_not_found_and_save_nothing_when_the_serial_does_not_exist(
    clean_readings: Engine,
) -> None:
    # Arrange
    client = build_api_client(clean_readings)

    # Act
    response = client.put("/api/pyrometers/ZZZZ.0000.0000", json={"nickname": "Forno"})

    # Assert
    assert response.status_code == 404
    assert client.get("/api/pyrometers").json() == []


def test_should_keep_the_previous_profile_when_the_new_one_is_invalid(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    client = build_api_client(clean_readings)
    client.put(f"/api/pyrometers/{PI_12}", json={"nickname": "Forno 2"})

    # Act
    response = client.put(f"/api/pyrometers/{PI_12}", json={"color": "vermelhão"})

    # Assert
    assert response.status_code == 422
    assert client.get("/api/pyrometers").json()[0]["nickname"] == "Forno 2"


def test_should_serve_the_summary_with_minutes_without_reading_when_clock_is_fixed(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12", 1500)
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 10, 5, 0), PI_12, "PI-12", 1510)
    client = build_api_client(clean_readings, FixedClock(datetime(2026, 10, 29, 10, 8, 0)))

    # Act
    body = client.get("/api/pyrometers/summary").json()

    # Assert
    assert body == [
        {
            "pyrometer_id": PI_12,
            "temperature": 1510,
            "measured_at": "2026-10-29T10:05:00",
            "battery": 63,
            "minutes_without_reading": 3,
        }
    ]


def test_should_not_alter_receiver_data_when_saving_and_querying(clean_readings: Engine) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 11, 0, 0), PI_14, "PI-14")
    before = snapshot_readings(clean_readings)
    client = build_api_client(clean_readings)

    # Act
    client.put(f"/api/pyrometers/{PI_12}", json={"nickname": "Forno 2"})
    client.get("/api/pyrometers")
    client.get("/api/pyrometers/summary")

    # Assert
    assert snapshot_readings(clean_readings) == before


def test_should_answer_pyrometers_and_summary_within_half_a_second_when_there_are_100k_readings(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_many_pyrometers(clean_readings, pyrometers=10, count=10_000, day=DAY)
    client = build_api_client(clean_readings, FixedClock(datetime(2026, 10, 30, 0, 0, 0)))

    # Act
    started = time.perf_counter()
    pyrometers = client.get("/api/pyrometers")
    summary = client.get("/api/pyrometers/summary")
    elapsed_each = (time.perf_counter() - started) / 2

    # Assert
    assert len(pyrometers.json()) == 10
    assert len(summary.json()) == 10
    assert elapsed_each <= 0.5


def test_should_answer_conflict_when_another_pyrometer_already_has_the_color(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 10, 0, 0), PI_14, "PI-14")
    client = build_api_client(clean_readings)
    client.put(f"/api/pyrometers/{PI_12}", json={"color": "#e11d48"})

    # Act
    response = client.put(f"/api/pyrometers/{PI_14}", json={"color": "#E11D48"})

    # Assert
    assert response.status_code == 409
    assert client.get("/api/pyrometers").json()[0]["color"] != "#e11d48"

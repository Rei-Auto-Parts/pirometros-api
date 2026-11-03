from datetime import datetime

from sqlalchemy import Engine

from tests.support.api_client import build_api_client
from tests.support.receiver_data_fixture import insert_reading

PERIOD = {"start": "2026-10-29T00:00:00", "end": "2026-10-29T23:59:59"}
PI_12 = "C24C.F90D.0000"
PI_14 = "B68A.1010.0000"


def test_should_serve_readings_with_local_date_when_period_is_given(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 11, 0, 30))
    client = build_api_client(clean_readings)

    # Act
    response = client.get("/api/readings", params=PERIOD)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["measured_at"] == "2026-10-29T11:00:30"
    assert body["items"][0]["gateway_name"] == "RERF"


def test_should_serve_series_grouped_by_pyrometer_when_period_is_given(
    clean_readings: Engine,
) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    insert_reading(clean_readings, 2, datetime(2026, 10, 29, 9, 0, 0), PI_14, "PI-14")
    client = build_api_client(clean_readings)

    # Act
    response = client.get("/api/readings/series", params=PERIOD)

    # Assert
    assert response.status_code == 200
    assert [item["pyrometer_name"] for item in response.json()] == ["PI-14", "PI-12"]


def test_should_serve_pyrometers_when_readings_exist(clean_readings: Engine) -> None:
    # Arrange
    insert_reading(clean_readings, 1, datetime(2026, 10, 29, 10, 0, 0), PI_12, "PI-12")
    client = build_api_client(clean_readings)

    # Act
    response = client.get("/api/pyrometers")

    # Assert
    assert response.json() == [{"id": PI_12, "name": "PI-12"}]


def test_should_respond_422_when_series_period_exceeds_31_days(clean_readings: Engine) -> None:
    # Arrange
    client = build_api_client(clean_readings)

    # Act
    response = client.get(
        "/api/readings/series",
        params={"start": "2026-10-01T00:00:00", "end": "2026-11-20T00:00:00"},
    )

    # Assert
    assert response.status_code == 422


def test_should_respond_503_when_database_is_down(clean_readings: Engine) -> None:
    # Arrange
    from infra.tools.database_tool import build_engine

    client = build_api_client(build_engine("postgresql+psycopg://x:x@127.0.0.1:1/x"))

    # Act
    response = client.get("/api/readings", params=PERIOD)

    # Assert
    assert response.status_code == 503
    assert response.json() == {"detail": "banco de dados indisponivel"}

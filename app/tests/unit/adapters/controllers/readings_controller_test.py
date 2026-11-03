from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.readings_controller import ReadingsController
from core.domain.dtos.pyrometer_series_dto import PyrometerSeriesDto
from core.domain.dtos.reading_dto import ReadingDto
from core.domain.dtos.readings_page_dto import ReadingsPageDto
from core.domain.errors.period_too_long_error import PeriodTooLongError
from interfaces.core.application.i_get_readings_series_use_case import IGetReadingsSeriesUseCase
from interfaces.core.application.i_list_readings_use_case import IListReadingsUseCase

PERIOD = {"start": "2026-10-29T00:00:00", "end": "2026-10-29T23:59:59"}


def build_reading() -> ReadingDto:
    return ReadingDto(
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


def build_client(
    list_use_case: IListReadingsUseCase, series_use_case: IGetReadingsSeriesUseCase
) -> TestClient:
    app = FastAPI()
    app.include_router(ReadingsController(list_use_case, series_use_case).router)
    return TestClient(app)


def build_mocks(mocker: MockerFixture) -> tuple[Mock, Mock]:
    list_use_case = mocker.Mock(spec=IListReadingsUseCase)
    list_use_case.execute.return_value = ReadingsPageDto((build_reading(),), 1, 1, 50)
    series_use_case = mocker.Mock(spec=IGetReadingsSeriesUseCase)
    series_use_case.execute.return_value = []
    return list_use_case, series_use_case


def test_should_return_page_with_all_reading_fields_when_listing(mocker: MockerFixture) -> None:
    # Arrange
    client = build_client(*build_mocks(mocker))

    # Act
    response = client.get("/readings", params=PERIOD)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 94,
                "gateway_id": "B571.430C.0000",
                "gateway_name": "RERF",
                "pyrometer_id": "C24C.F90D.0000",
                "pyrometer_name": "PI-12",
                "measured_at": "2026-10-29T11:00:30",
                "thermocouple": "S",
                "unit": "Celsius",
                "cold_junction": 31.4,
                "read_delay": 0,
                "place": 60,
                "battery": 63,
                "temperature": 1548,
                "detect_time": 3.9,
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 50,
    }


def test_should_use_default_page_when_page_is_not_informed(mocker: MockerFixture) -> None:
    # Arrange
    list_use_case, series_use_case = build_mocks(mocker)
    client = build_client(list_use_case, series_use_case)

    # Act
    client.get("/readings", params=PERIOD)

    # Assert
    list_use_case.execute.assert_called_once_with(
        datetime(2026, 10, 29, 0, 0, 0),
        datetime(2026, 10, 29, 23, 59, 59),
        [],
        page=1,
        page_size=50,
    )


def test_should_pass_pyrometer_filter_when_dev_id_is_repeated(mocker: MockerFixture) -> None:
    # Arrange
    list_use_case, series_use_case = build_mocks(mocker)
    client = build_client(list_use_case, series_use_case)

    # Act
    client.get("/readings", params={**PERIOD, "dev_id": ["A", "B"], "page": 2, "page_size": 10})

    # Assert
    list_use_case.execute.assert_called_once_with(
        datetime(2026, 10, 29, 0, 0, 0),
        datetime(2026, 10, 29, 23, 59, 59),
        ["A", "B"],
        page=2,
        page_size=10,
    )


@pytest.mark.parametrize(
    "params",
    [
        {**PERIOD, "page_size": 501},
        {**PERIOD, "page_size": 0},
        {**PERIOD, "page": 0},
        {"end": PERIOD["end"]},
        {"start": PERIOD["start"]},
        {"start": "2026-10-29T00:00:00Z", "end": "2026-10-29T23:59:59Z"},
    ],
)
def test_should_respond_422_without_listing_when_parameters_are_invalid(
    mocker: MockerFixture, params: dict[str, object]
) -> None:
    # Arrange
    list_use_case, series_use_case = build_mocks(mocker)
    client = build_client(list_use_case, series_use_case)

    # Act
    response = client.get("/readings", params=params)

    # Assert
    assert response.status_code == 422
    list_use_case.execute.assert_not_called()


def test_should_group_points_by_pyrometer_when_requesting_series(mocker: MockerFixture) -> None:
    # Arrange
    list_use_case, series_use_case = build_mocks(mocker)
    series_use_case.execute.return_value = [
        PyrometerSeriesDto("C24C.F90D.0000", "PI-12", (build_reading(),))
    ]
    client = build_client(list_use_case, series_use_case)

    # Act
    response = client.get("/readings/series", params=PERIOD)

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "pyrometer_id": "C24C.F90D.0000",
            "pyrometer_name": "PI-12",
            "points": [
                {"id": 94, "measured_at": "2026-10-29T11:00:30", "temperature": 1548, "place": 60}
            ],
        }
    ]


def test_should_pass_period_and_filter_when_requesting_series(mocker: MockerFixture) -> None:
    # Arrange
    list_use_case, series_use_case = build_mocks(mocker)
    client = build_client(list_use_case, series_use_case)

    # Act
    client.get("/readings/series", params={**PERIOD, "dev_id": ["A"]})

    # Assert
    series_use_case.execute.assert_called_once_with(
        datetime(2026, 10, 29, 0, 0, 0), datetime(2026, 10, 29, 23, 59, 59), ["A"]
    )


def test_should_respond_422_with_limit_when_series_period_is_too_long(
    mocker: MockerFixture,
) -> None:
    # Arrange
    list_use_case, series_use_case = build_mocks(mocker)
    series_use_case.execute.side_effect = PeriodTooLongError(31)
    client = build_client(list_use_case, series_use_case)

    # Act
    response = client.get("/readings/series", params=PERIOD)

    # Assert
    assert response.status_code == 422
    assert "31" in response.json()["detail"]

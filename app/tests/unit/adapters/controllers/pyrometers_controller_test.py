from datetime import datetime
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.pyrometers_controller import PyrometersController
from core.domain.dtos.pyrometer_overview_dto import PyrometerOverviewDto
from core.domain.dtos.pyrometer_summary_dto import PyrometerSummaryDto
from core.domain.errors.color_in_use_error import ColorInUseError
from core.domain.errors.pyrometer_not_found_error import PyrometerNotFoundError
from interfaces.core.application.i_list_pyrometer_summaries_use_case import (
    IListPyrometerSummariesUseCase,
)
from interfaces.core.application.i_list_pyrometers_use_case import IListPyrometersUseCase
from interfaces.core.application.i_save_pyrometer_profile_use_case import (
    ISavePyrometerProfileUseCase,
)

PI12 = "C24C.F90D.0000"
PI14 = "B68A.1010.0000"
FORNO = PyrometerOverviewDto(PI12, "PI-12", "Forno 2", "#e11d48", "nota", True)
SEM_COMPLEMENTO = PyrometerOverviewDto(PI14, "PI-14", None, "#2563eb", None, True)


def build_client(
    mocker: MockerFixture, overview: list[PyrometerOverviewDto] | None = None
) -> tuple[TestClient, Mock, Mock, Mock]:
    list_use_case = mocker.Mock(spec=IListPyrometersUseCase)
    list_use_case.execute.return_value = overview if overview is not None else []
    summaries = mocker.Mock(spec=IListPyrometerSummariesUseCase)
    summaries.execute.return_value = []
    save = mocker.Mock(spec=ISavePyrometerProfileUseCase)
    app = FastAPI()
    app.include_router(PyrometersController(list_use_case, summaries, save).router)
    return TestClient(app), list_use_case, summaries, save


def test_should_return_the_profile_fields_when_listing_pyrometers(mocker: MockerFixture) -> None:
    # Arrange
    client, _, _, _ = build_client(mocker, [FORNO, SEM_COMPLEMENTO])

    # Act
    response = client.get("/pyrometers")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": PI12,
            "name": "PI-12",
            "nickname": "Forno 2",
            "color": "#e11d48",
            "note": "nota",
            "active": True,
        },
        {
            "id": PI14,
            "name": "PI-14",
            "nickname": None,
            "color": "#2563eb",
            "note": None,
            "active": True,
        },
    ]


def test_should_execute_list_use_case_once_when_listing_pyrometers(mocker: MockerFixture) -> None:
    # Arrange
    client, list_use_case, _, _ = build_client(mocker)

    # Act
    client.get("/pyrometers")

    # Assert
    list_use_case.execute.assert_called_once_with()


def test_should_return_summaries_without_timezone_when_asking_for_the_summary(
    mocker: MockerFixture,
) -> None:
    # Arrange
    client, _, summaries, _ = build_client(mocker)
    summaries.execute.return_value = [
        PyrometerSummaryDto(PI12, 1510, datetime(2026, 11, 5, 10, 5, 0), 62, 3)
    ]

    # Act
    response = client.get("/pyrometers/summary")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {
            "pyrometer_id": PI12,
            "temperature": 1510,
            "measured_at": "2026-11-05T10:05:00",
            "battery": 62,
            "minutes_without_reading": 3,
        }
    ]
    summaries.execute.assert_called_once_with()


def test_should_save_and_return_the_pyrometer_when_putting_a_profile(
    mocker: MockerFixture,
) -> None:
    # Arrange
    client, _, _, save = build_client(mocker, [FORNO])
    body = {"nickname": "Forno 2", "color": "#e11d48", "note": "nota", "active": True}

    # Act
    response = client.put(f"/pyrometers/{PI12}", json=body)

    # Assert
    assert response.status_code == 200
    assert response.json()["nickname"] == "Forno 2"
    save.execute.assert_called_once_with(PI12, "Forno 2", "#e11d48", "nota", True)


def test_should_default_to_active_with_no_fields_when_putting_an_empty_body(
    mocker: MockerFixture,
) -> None:
    # Arrange
    client, _, _, save = build_client(mocker, [SEM_COMPLEMENTO])

    # Act
    response = client.put(f"/pyrometers/{PI14}", json={})

    # Assert
    assert response.status_code == 200
    save.execute.assert_called_once_with(PI14, None, None, None, True)


def test_should_answer_not_found_when_the_serial_does_not_exist(mocker: MockerFixture) -> None:
    # Arrange
    client, _, _, save = build_client(mocker)
    save.execute.side_effect = PyrometerNotFoundError("ZZZZ.0000.0000")

    # Act
    response = client.put("/pyrometers/ZZZZ.0000.0000", json={"nickname": "Forno"})

    # Assert
    assert response.status_code == 404
    assert "ZZZZ.0000.0000" in response.json()["detail"]


def test_should_reject_when_the_color_is_not_hexadecimal(mocker: MockerFixture) -> None:
    # Arrange
    client, _, _, save = build_client(mocker, [FORNO])

    # Act
    response = client.put(f"/pyrometers/{PI12}", json={"color": "vermelhão"})

    # Assert
    assert response.status_code == 422
    save.execute.assert_not_called()


def test_should_reject_when_the_nickname_has_more_than_40_characters(
    mocker: MockerFixture,
) -> None:
    # Arrange
    client, _, _, save = build_client(mocker, [FORNO])

    # Act
    response = client.put(f"/pyrometers/{PI12}", json={"nickname": "x" * 41})

    # Assert
    assert response.status_code == 422
    save.execute.assert_not_called()


def test_should_reject_when_the_note_has_more_than_500_characters(mocker: MockerFixture) -> None:
    # Arrange
    client, _, _, save = build_client(mocker, [FORNO])

    # Act
    response = client.put(f"/pyrometers/{PI12}", json={"note": "x" * 501})

    # Assert
    assert response.status_code == 422
    save.execute.assert_not_called()


def test_should_accept_the_limit_sizes_when_putting_a_profile(mocker: MockerFixture) -> None:
    # Arrange
    client, _, _, save = build_client(mocker, [FORNO])
    body = {"nickname": "x" * 40, "note": "y" * 500}

    # Act
    response = client.put(f"/pyrometers/{PI12}", json=body)

    # Assert
    assert response.status_code == 200
    save.execute.assert_called_once_with(PI12, "x" * 40, None, "y" * 500, True)


def test_should_answer_conflict_when_the_color_is_in_use(mocker: MockerFixture) -> None:
    # Arrange
    client, _, _, save = build_client(mocker)
    save.execute.side_effect = ColorInUseError("#e11d48")

    # Act
    response = client.put(f"/pyrometers/{PI12}", json={"color": "#e11d48"})

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "a cor '#e11d48' ja esta em uso por outro pirometro"

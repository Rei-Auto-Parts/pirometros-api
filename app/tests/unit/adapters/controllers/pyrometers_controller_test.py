from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.pyrometers_controller import PyrometersController
from core.domain.dtos.pyrometer_dto import PyrometerDto
from interfaces.core.application.i_list_pyrometers_use_case import IListPyrometersUseCase


def build_client(use_case: IListPyrometersUseCase) -> TestClient:
    app = FastAPI()
    app.include_router(PyrometersController(use_case).router)
    return TestClient(app)


def test_should_return_serial_and_name_when_listing_pyrometers(mocker: MockerFixture) -> None:
    # Arrange
    use_case = mocker.Mock(spec=IListPyrometersUseCase)
    use_case.execute.return_value = [
        PyrometerDto("C24C.F90D.0000", "PI-12"),
        PyrometerDto("B68A.1010.0000", "PI-14"),
    ]
    client = build_client(use_case)

    # Act
    response = client.get("/pyrometers")

    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {"id": "C24C.F90D.0000", "name": "PI-12"},
        {"id": "B68A.1010.0000", "name": "PI-14"},
    ]


def test_should_execute_use_case_once_when_listing_pyrometers(mocker: MockerFixture) -> None:
    # Arrange
    use_case = mocker.Mock(spec=IListPyrometersUseCase)
    use_case.execute.return_value = []
    client = build_client(use_case)

    # Act
    client.get("/pyrometers")

    # Assert
    use_case.execute.assert_called_once_with()

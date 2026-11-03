from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.health_controller import HealthController
from adapters.controllers.pyrometers_controller import PyrometersController
from adapters.controllers.readings_controller import ReadingsController
from infra.api.api_router import build_api_router
from interfaces.core.application.i_check_health_use_case import ICheckHealthUseCase
from interfaces.core.application.i_get_readings_series_use_case import IGetReadingsSeriesUseCase
from interfaces.core.application.i_list_pyrometers_use_case import IListPyrometersUseCase
from interfaces.core.application.i_list_readings_use_case import IListReadingsUseCase


def test_should_expose_every_controller_under_api_prefix_when_router_is_built(
    mocker: MockerFixture,
) -> None:
    # Arrange
    router = build_api_router(
        HealthController(mocker.Mock(spec=ICheckHealthUseCase)),
        ReadingsController(
            mocker.Mock(spec=IListReadingsUseCase), mocker.Mock(spec=IGetReadingsSeriesUseCase)
        ),
        PyrometersController(mocker.Mock(spec=IListPyrometersUseCase)),
    )
    app = FastAPI()
    app.include_router(router)

    # Act
    paths = set(app.openapi()["paths"])

    # Assert
    assert {"/api/health", "/api/readings", "/api/readings/series", "/api/pyrometers"} <= paths


def test_should_not_expose_routes_outside_api_prefix_when_router_is_built(
    mocker: MockerFixture,
) -> None:
    # Arrange
    app = FastAPI()
    app.include_router(
        build_api_router(PyrometersController(mocker.Mock(spec=IListPyrometersUseCase)))
    )
    client = TestClient(app)

    # Act
    response = client.get("/pyrometers")

    # Assert
    assert response.status_code == 404

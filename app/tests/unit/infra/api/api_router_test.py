from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.health_controller import HealthController
from adapters.controllers.pyrometers_controller import PyrometersController
from adapters.controllers.readings_controller import ReadingsController
from infra.api.api_router import build_api_router
from interfaces.core.application.i_check_health_use_case import ICheckHealthUseCase
from interfaces.core.application.i_get_readings_series_use_case import IGetReadingsSeriesUseCase
from interfaces.core.application.i_list_pyrometer_summaries_use_case import (
    IListPyrometerSummariesUseCase,
)
from interfaces.core.application.i_list_pyrometers_use_case import IListPyrometersUseCase
from interfaces.core.application.i_list_readings_use_case import IListReadingsUseCase
from interfaces.core.application.i_save_pyrometer_profile_use_case import (
    ISavePyrometerProfileUseCase,
)


def build_pyrometers_controller(mocker: MockerFixture) -> PyrometersController:
    return PyrometersController(
        mocker.Mock(spec=IListPyrometersUseCase),
        mocker.Mock(spec=IListPyrometerSummariesUseCase),
        mocker.Mock(spec=ISavePyrometerProfileUseCase),
    )


def test_should_expose_every_controller_under_api_prefix_when_router_is_built(
    mocker: MockerFixture,
) -> None:
    # Arrange
    router = build_api_router(
        HealthController(mocker.Mock(spec=ICheckHealthUseCase)),
        ReadingsController(
            mocker.Mock(spec=IListReadingsUseCase), mocker.Mock(spec=IGetReadingsSeriesUseCase)
        ),
        build_pyrometers_controller(mocker),
    )
    app = FastAPI()
    app.include_router(router)

    # Act
    paths = set(app.openapi()["paths"])

    # Assert
    assert {
        "/api/health",
        "/api/readings",
        "/api/readings/series",
        "/api/pyrometers",
        "/api/pyrometers/summary",
        "/api/pyrometers/{pyrometer_id}",
    } <= paths


def test_should_not_expose_routes_outside_api_prefix_when_router_is_built(
    mocker: MockerFixture,
) -> None:
    # Arrange
    app = FastAPI()
    app.include_router(build_api_router(build_pyrometers_controller(mocker)))
    client = TestClient(app)

    # Act
    response = client.get("/pyrometers")

    # Assert
    assert response.status_code == 404

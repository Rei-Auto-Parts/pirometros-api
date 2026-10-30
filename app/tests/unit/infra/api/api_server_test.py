from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.health_controller import HealthController
from core.domain.dtos.health_status_dto import HealthStatusDto
from infra.api.api_router import build_api_router
from infra.api.api_server import create_app
from interfaces.core.application.i_check_health_use_case import ICheckHealthUseCase


def build_client(mocker: MockerFixture) -> TestClient:
    use_case = mocker.Mock(spec=ICheckHealthUseCase)
    use_case.execute.return_value = HealthStatusDto(api_up=True, database_up=True)
    return TestClient(create_app(build_api_router(HealthController(use_case))))


def test_should_serve_openapi_docs_when_path_is_api_docs(mocker: MockerFixture) -> None:
    # Arrange
    client = build_client(mocker)

    # Act
    response = client.get("/api/docs")

    # Assert
    assert response.status_code == 200


def test_should_not_serve_docs_when_path_is_outside_api(mocker: MockerFixture) -> None:
    # Arrange
    client = build_client(mocker)

    # Act
    response = client.get("/docs")

    # Assert
    assert response.status_code == 404


def test_should_serve_health_under_api_prefix_when_app_is_built(mocker: MockerFixture) -> None:
    # Arrange
    client = build_client(mocker)

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200

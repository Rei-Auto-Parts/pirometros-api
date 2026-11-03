from fastapi import APIRouter
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.exc import OperationalError

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


def build_failing_client() -> TestClient:
    router = APIRouter()

    @router.get("/boom")
    def boom() -> None:
        raise OperationalError("SELECT 1", {}, Exception("senha=secreta"))

    return TestClient(create_app(router))


def test_should_respond_503_without_driver_message_when_database_fails() -> None:
    # Arrange
    client = build_failing_client()

    # Act
    response = client.get("/boom")

    # Assert
    assert response.status_code == 503
    assert response.json() == {"detail": "banco de dados indisponivel"}


def test_should_log_only_error_type_when_database_fails(mocker: MockerFixture) -> None:
    # Arrange
    logger = mocker.patch("infra.api.api_server.LOGGER")
    client = build_failing_client()

    # Act
    client.get("/boom")

    # Assert
    logger.warning.assert_called_once_with("database error: %s", "OperationalError")


def test_should_serve_health_under_api_prefix_when_app_is_built(mocker: MockerFixture) -> None:
    # Arrange
    client = build_client(mocker)

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200

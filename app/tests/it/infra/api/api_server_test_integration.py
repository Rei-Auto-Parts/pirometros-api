import logging
import os

from fastapi.testclient import TestClient

from adapters.controllers.health_controller import HealthController
from adapters.repositories.database_health_repository import DatabaseHealthRepository
from core.application.check_health_use_case import CheckHealthUseCase
from infra.api.api_router import build_api_router
from infra.api.api_server import create_app
from infra.tools.database_tool import build_engine


def build_client(database_url: str) -> TestClient:
    repository = DatabaseHealthRepository(build_engine(database_url), logging.getLogger("it"))
    controller = HealthController(CheckHealthUseCase(repository))
    return TestClient(create_app(build_api_router(controller)))


def test_should_report_database_up_when_postgres_is_reachable() -> None:
    # Arrange
    client = build_client(os.environ["DATABASE_URL"])

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.json() == {"api": "up", "database": "up"}


def test_should_report_database_down_when_postgres_is_unreachable() -> None:
    # Arrange
    client = build_client("postgresql+psycopg://x:x@127.0.0.1:1/x")

    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"api": "up", "database": "down"}

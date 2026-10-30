import logging
import os
from typing import Any

from behave import given, then, when
from fastapi.testclient import TestClient

from adapters.controllers.health_controller import HealthController
from adapters.repositories.database_health_repository import DatabaseHealthRepository
from core.application.check_health_use_case import CheckHealthUseCase
from infra.api.api_router import build_api_router
from infra.api.api_server import create_app
from infra.tools.database_tool import build_engine

UNREACHABLE_URL = "postgresql+psycopg://x:x@127.0.0.1:1/x"


def build_client(database_url: str) -> TestClient:
    repository = DatabaseHealthRepository(build_engine(database_url), logging.getLogger("bdd"))
    controller = HealthController(CheckHealthUseCase(repository))
    return TestClient(create_app(build_api_router(controller)))


@given("que o banco de dados esta acessivel")
def database_reachable(context: Any) -> None:
    context.client = build_client(os.environ["DATABASE_URL"])


@given("que o banco de dados esta inacessivel")
def database_unreachable(context: Any) -> None:
    context.client = build_client(UNREACHABLE_URL)


@when("eu consulto a saude da API")
def request_health(context: Any) -> None:
    context.response = context.client.get("/api/health")


@then("a API responde com status {status:d}")
def check_status(context: Any, status: int) -> None:
    assert context.response.status_code == status


@then('a resposta informa api "{api}" e banco "{database}"')
def check_body(context: Any, api: str, database: str) -> None:
    assert context.response.json() == {"api": api, "database": database}

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from adapters.controllers.health_controller import HealthController
from core.domain.dtos.health_status_dto import HealthStatusDto
from interfaces.core.application.i_check_health_use_case import ICheckHealthUseCase


def build_client(use_case: ICheckHealthUseCase) -> TestClient:
    app = FastAPI()
    app.include_router(HealthController(use_case).router)
    return TestClient(app)


@pytest.mark.parametrize(
    ("database_up", "expected"),
    [(True, {"api": "up", "database": "up"}), (False, {"api": "up", "database": "down"})],
)
def test_should_respond_200_with_each_part_state_when_health_is_requested(
    mocker: MockerFixture, database_up: bool, expected: dict[str, str]
) -> None:
    # Arrange
    use_case = mocker.Mock(spec=ICheckHealthUseCase)
    use_case.execute.return_value = HealthStatusDto(api_up=True, database_up=database_up)
    client = build_client(use_case)

    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_should_execute_use_case_once_when_health_is_requested(mocker: MockerFixture) -> None:
    # Arrange
    use_case = mocker.Mock(spec=ICheckHealthUseCase)
    use_case.execute.return_value = HealthStatusDto(api_up=True, database_up=True)
    client = build_client(use_case)

    # Act
    client.get("/health")

    # Assert
    use_case.execute.assert_called_once_with()

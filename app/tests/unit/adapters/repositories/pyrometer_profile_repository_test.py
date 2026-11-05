from typing import Any

from pytest_mock import MockerFixture
from sqlalchemy import Engine

from adapters.repositories.pyrometer_profile_repository import PyrometerProfileRepository
from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto

PI12 = "C24C.F90D.0000"


def build_repository(
    mocker: MockerFixture, rows: list[dict[str, Any]]
) -> tuple[PyrometerProfileRepository, Any]:
    engine = mocker.MagicMock(spec=Engine)
    connection = engine.connect.return_value.__enter__.return_value
    connection.execute.return_value.mappings.return_value.all.return_value = rows
    begin_connection = engine.begin.return_value.__enter__.return_value
    return PyrometerProfileRepository(engine), (connection, begin_connection)


def test_should_map_rows_to_profiles_when_finding_all(mocker: MockerFixture) -> None:
    # Arrange
    row = {
        "pyrometer_id": PI12,
        "nickname": "Forno 2",
        "color": "#e11d48",
        "note": "termopar trocado",
        "active": False,
    }
    repository, _ = build_repository(mocker, [row])

    # Act
    result = repository.find_all()

    # Assert
    assert result == [PyrometerProfileDto(PI12, "Forno 2", "#e11d48", "termopar trocado", False)]


def test_should_only_select_from_the_app_schema_when_finding_all(mocker: MockerFixture) -> None:
    # Arrange
    repository, (connection, _) = build_repository(mocker, [])

    # Act
    repository.find_all()

    # Assert
    statement = str(connection.execute.call_args.args[0])
    assert statement.lstrip().upper().startswith("SELECT")
    assert "app.pyrometer_profile" in statement
    assert "receiver_data" not in statement


def test_should_upsert_into_the_app_schema_when_saving(mocker: MockerFixture) -> None:
    # Arrange
    repository, (_, writer) = build_repository(mocker, [])
    profile = PyrometerProfileDto(PI12, "Forno 2", "#e11d48", "nota", True)

    # Act
    repository.save(profile)

    # Assert
    writer.execute.assert_called_once()
    statement, params = writer.execute.call_args.args
    assert "INSERT INTO app.pyrometer_profile" in str(statement)
    assert "ON CONFLICT (pyrometer_id) DO UPDATE" in str(statement)
    assert "receiver_data" not in str(statement)
    assert params == {
        "pyrometer_id": PI12,
        "nickname": "Forno 2",
        "color": "#e11d48",
        "note": "nota",
        "active": True,
    }

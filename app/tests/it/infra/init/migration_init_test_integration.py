import os

from sqlalchemy import text

from infra.init.migration_init import run_migrations
from infra.tools.database_tool import build_engine

URL = os.environ["DATABASE_URL"]


def public_tables() -> list[str]:
    with build_engine(URL).connect() as connection:
        rows = connection.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        return sorted(row[0] for row in rows)


def test_should_create_schema_app_with_version_table_when_migrations_run() -> None:
    # Arrange / Act
    run_migrations(URL)

    # Assert
    with build_engine(URL).connect() as connection:
        schemas = connection.execute(text("SELECT schema_name FROM information_schema.schemata"))
        version = connection.execute(text("SELECT version_num FROM app.alembic_version"))
        assert "app" in [row[0] for row in schemas]
        assert [row[0] for row in version] == ["0002"]


def test_should_leave_public_schema_untouched_when_migrations_run() -> None:
    # Arrange
    before = public_tables()

    # Act
    run_migrations(URL)

    # Assert
    assert public_tables() == before
    assert "alembic_version" not in before


def test_should_be_idempotent_when_migrations_run_twice() -> None:
    # Arrange
    run_migrations(URL)

    # Act
    run_migrations(URL)

    # Assert
    with build_engine(URL).connect() as connection:
        count = connection.execute(text("SELECT count(*) FROM app.alembic_version")).scalar_one()
        assert count == 1


def test_should_create_the_pyrometer_profile_table_in_schema_app_when_migrations_run() -> None:
    # Arrange / Act
    run_migrations(URL)

    # Assert
    with build_engine(URL).connect() as connection:
        columns = connection.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'app' AND table_name = 'pyrometer_profile'"
            )
        )
        assert {row[0] for row in columns} == {
            "pyrometer_id",
            "nickname",
            "color",
            "note",
            "active",
            "updated_at",
        }

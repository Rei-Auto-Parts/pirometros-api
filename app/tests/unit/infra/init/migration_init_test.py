from alembic import command
from alembic.config import Config
from pytest_mock import MockerFixture

from infra.init.migration_init import MIGRATIONS_DIR, run_migrations


def test_should_upgrade_to_head_when_migrations_run(mocker: MockerFixture) -> None:
    # Arrange
    upgrade = mocker.patch.object(command, "upgrade")

    # Act
    run_migrations("postgresql+psycopg://u:p%40ss@host/db")

    # Assert
    upgrade.assert_called_once_with(mocker.ANY, "head")


def test_should_pass_url_and_script_location_when_migrations_run(mocker: MockerFixture) -> None:
    # Arrange
    upgrade = mocker.patch.object(command, "upgrade")
    url = "postgresql+psycopg://u:p%40ss@host/db"

    # Act
    run_migrations(url)

    # Assert
    config: Config = upgrade.call_args.args[0]
    assert config.attributes["url"] == url
    assert config.get_main_option("script_location") == str(MIGRATIONS_DIR)

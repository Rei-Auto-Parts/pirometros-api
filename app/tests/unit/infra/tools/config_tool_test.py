import pytest

from infra.tools.config_tool import Settings


def test_should_read_database_url_as_secret_when_env_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:s@h/db")

    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert settings.database_url.get_secret_value() == "postgresql+psycopg://u:s@h/db"
    assert "s@h" not in repr(settings)


def test_should_use_defaults_when_only_database_url_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:s@h/db")
    monkeypatch.delenv("PORT", raising=False)

    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert (settings.port, settings.log_level, settings.run_migrations_on_start) == (
        8000,
        "INFO",
        True,
    )
    assert settings.local_timezone == "America/Sao_Paulo"


def test_should_read_local_timezone_when_env_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:s@h/db")
    monkeypatch.setenv("LOCAL_TIMEZONE", "UTC")

    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert settings.local_timezone == "UTC"


def test_should_fail_when_database_url_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Act / Assert
    with pytest.raises(ValueError, match="database_url"):
        Settings(_env_file=None)

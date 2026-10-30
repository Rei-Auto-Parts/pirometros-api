from infra.tools.database_tool import build_engine


def test_should_build_lazy_engine_for_given_url_when_requested() -> None:
    # Act
    engine = build_engine("postgresql+psycopg://u:s@127.0.0.1:1/db")

    # Assert
    assert engine.url.host == "127.0.0.1"
    assert engine.url.database == "db"
    assert engine.dialect.driver == "psycopg"

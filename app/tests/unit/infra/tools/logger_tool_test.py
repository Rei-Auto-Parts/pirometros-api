import json
import logging

from infra.tools.logger_tool import JsonFormatter, configure_logging, get_logger


def test_should_format_record_as_json_when_formatter_runs() -> None:
    # Arrange
    record = logging.LogRecord("pir", logging.WARNING, "f.py", 1, "olá %s", ("mundo",), None)

    # Act
    payload = json.loads(JsonFormatter().format(record))

    # Assert
    assert (payload["level"], payload["logger"], payload["message"]) == (
        "WARNING",
        "pir",
        "olá mundo",
    )
    assert payload["ts"].endswith("+00:00")


def test_should_install_single_json_handler_when_logging_is_configured() -> None:
    # Arrange
    root = logging.getLogger()
    previous = (root.handlers, root.level)

    # Act
    configure_logging("debug")
    configure_logging("debug")

    # Assert
    try:
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)
        assert root.level == logging.DEBUG
    finally:
        root.handlers, root.level = previous[0], previous[1]


def test_should_return_named_logger_when_requested() -> None:
    # Act
    logger = get_logger("database")

    # Assert
    assert logger.name == "database"

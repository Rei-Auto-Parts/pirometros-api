from datetime import timedelta
from zoneinfo import ZoneInfoNotFoundError

import pytest

from infra.tools.clock_tool import ClockTool


def test_should_return_a_naive_datetime_when_asking_for_now() -> None:
    # Arrange
    clock = ClockTool("America/Sao_Paulo")

    # Act
    now = clock.now()

    # Assert
    assert now.tzinfo is None


def test_should_follow_the_configured_timezone_when_asking_for_now() -> None:
    # Arrange
    tokyo = ClockTool("Asia/Tokyo")
    utc = ClockTool("UTC")

    # Act
    difference = tokyo.now() - utc.now()

    # Assert
    assert timedelta(hours=9) - timedelta(seconds=5) < difference < timedelta(hours=9, seconds=5)


def test_should_fail_when_the_timezone_is_unknown() -> None:
    # Arrange / Act / Assert
    with pytest.raises(ZoneInfoNotFoundError):
        ClockTool("Marte/Olympus")

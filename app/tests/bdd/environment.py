import os
from datetime import datetime
from typing import Any

from tests.support.api_client import build_api_client
from tests.support.fixed_clock import FixedClock
from tests.support.receiver_data_fixture import (
    build_test_engine,
    clear_profiles,
    clear_readings,
)


def before_all(context: Any) -> None:
    context.engine = build_test_engine(os.environ["DATABASE_URL"])
    context.clock = FixedClock(datetime(2026, 11, 5, 12, 0, 0))
    context.client = build_api_client(context.engine, context.clock)


def before_scenario(context: Any, _scenario: Any) -> None:
    clear_readings(context.engine)
    clear_profiles(context.engine)

import os
from typing import Any

from tests.support.api_client import build_api_client
from tests.support.receiver_data_fixture import build_test_engine, clear_readings


def before_all(context: Any) -> None:
    context.engine = build_test_engine(os.environ["DATABASE_URL"])
    context.client = build_api_client(context.engine)


def before_scenario(context: Any, _scenario: Any) -> None:
    clear_readings(context.engine)

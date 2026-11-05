import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine

from tests.support.receiver_data_fixture import (
    build_test_engine,
    clear_profiles,
    clear_readings,
)


@pytest.fixture(scope="session")
def engine() -> Engine:
    return build_test_engine(os.environ["DATABASE_URL"])


@pytest.fixture
def clean_readings(engine: Engine) -> Iterator[Engine]:
    clear_readings(engine)
    clear_profiles(engine)
    yield engine
    clear_readings(engine)
    clear_profiles(engine)

from __future__ import annotations

import logging

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from adapters.controllers.health_controller import HealthController
from adapters.controllers.pyrometers_controller import PyrometersController
from adapters.controllers.readings_controller import ReadingsController
from adapters.repositories.database_health_repository import DatabaseHealthRepository
from adapters.repositories.pyrometer_profile_repository import PyrometerProfileRepository
from adapters.repositories.reading_repository import ReadingRepository
from core.application.check_health_use_case import CheckHealthUseCase
from core.application.get_readings_series_use_case import GetReadingsSeriesUseCase
from core.application.list_pyrometer_summaries_use_case import ListPyrometerSummariesUseCase
from core.application.list_pyrometers_use_case import ListPyrometersUseCase
from core.application.list_readings_use_case import ListReadingsUseCase
from core.application.save_pyrometer_profile_use_case import SavePyrometerProfileUseCase
from infra.api.api_router import build_api_router
from infra.api.api_server import create_app
from infra.tools.clock_tool import ClockTool
from interfaces.infra.tools.i_clock_tool import IClockTool


def build_api_client(engine: Engine, clock: IClockTool | None = None) -> TestClient:
    """A API inteira com as implementacoes reais, apontando para o banco de teste."""
    reading_repository = ReadingRepository(engine)
    profile_repository = PyrometerProfileRepository(engine)
    clock = clock or ClockTool("America/Sao_Paulo")
    router = build_api_router(
        HealthController(
            CheckHealthUseCase(DatabaseHealthRepository(engine, logging.getLogger("t")))
        ),
        ReadingsController(
            ListReadingsUseCase(reading_repository), GetReadingsSeriesUseCase(reading_repository)
        ),
        PyrometersController(
            ListPyrometersUseCase(reading_repository, profile_repository),
            ListPyrometerSummariesUseCase(reading_repository, clock),
            SavePyrometerProfileUseCase(reading_repository, profile_repository),
        ),
    )
    return TestClient(create_app(router))

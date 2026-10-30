from adapters.controllers.health_controller import HealthController
from adapters.repositories.database_health_repository import DatabaseHealthRepository
from core.application.check_health_use_case import CheckHealthUseCase
from infra.api.api_entry import ApiEntry
from infra.api.api_router import build_api_router
from infra.api.api_server import create_app
from infra.init.migration_init import run_migrations
from infra.tools.config_tool import Settings
from infra.tools.database_tool import build_engine
from infra.tools.logger_tool import configure_logging, get_logger


def build_api_entry() -> ApiEntry:
    """Monta a aplicacao com as implementacoes concretas. Fora da conta de cobertura."""
    settings = Settings()  # type: ignore[call-arg]
    configure_logging(settings.log_level)
    database_url = settings.database_url.get_secret_value()

    repository = DatabaseHealthRepository(build_engine(database_url), get_logger("database"))
    health_controller = HealthController(CheckHealthUseCase(repository))
    app = create_app(build_api_router(health_controller))

    def before_start() -> None:
        if settings.run_migrations_on_start:
            run_migrations(database_url)

    return ApiEntry(app, "0.0.0.0", settings.port, before_start)

from __future__ import annotations

from fastapi import APIRouter

from adapters.controllers.health_controller import HealthController
from adapters.controllers.pyrometers_controller import PyrometersController
from adapters.controllers.readings_controller import ReadingsController


def build_api_router(
    *controllers: HealthController | ReadingsController | PyrometersController,
) -> APIRouter:
    """Todas as rotas da API moram sob `/api`."""
    router = APIRouter(prefix="/api")
    for controller in controllers:
        router.include_router(controller.router)
    return router

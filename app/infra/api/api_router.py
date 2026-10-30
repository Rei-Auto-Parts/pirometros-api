from __future__ import annotations

from fastapi import APIRouter

from adapters.controllers.health_controller import HealthController


def build_api_router(health_controller: HealthController) -> APIRouter:
    """Todas as rotas da API moram sob `/api`."""
    router = APIRouter(prefix="/api")
    router.include_router(health_controller.router)
    return router

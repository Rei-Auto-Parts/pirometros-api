from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from interfaces.core.application.i_check_health_use_case import ICheckHealthUseCase


class HealthResponse(BaseModel):
    api: Literal["up"]
    database: Literal["up", "down"]


class HealthController:
    """GET /health: responde 200 mesmo com o banco fora, informando o estado de cada parte."""

    def __init__(self, check_health_use_case: ICheckHealthUseCase) -> None:
        self._check_health_use_case = check_health_use_case
        self.router = APIRouter(tags=["saude"])
        self.router.add_api_route(
            "/health",
            self.get_health,
            methods=["GET"],
            response_model=HealthResponse,
            summary="Estado da API e do banco de dados",
        )

    def get_health(self) -> HealthResponse:
        status = self._check_health_use_case.execute()
        return HealthResponse(api="up", database="up" if status.database_up else "down")

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from interfaces.core.application.i_list_pyrometers_use_case import IListPyrometersUseCase


class PyrometerResponse(BaseModel):
    id: str
    name: str | None


class PyrometersController:
    """GET /pyrometers: os pirometros existentes, com serial e nome atual."""

    def __init__(self, list_pyrometers_use_case: IListPyrometersUseCase) -> None:
        self._list_pyrometers_use_case = list_pyrometers_use_case
        self.router = APIRouter(tags=["pirometros"])
        self.router.add_api_route(
            "/pyrometers",
            self.list_pyrometers,
            methods=["GET"],
            response_model=list[PyrometerResponse],
            summary="Pirometros existentes",
        )

    def list_pyrometers(self) -> list[PyrometerResponse]:
        return [
            PyrometerResponse(id=pyrometer.id, name=pyrometer.name)
            for pyrometer in self._list_pyrometers_use_case.execute()
        ]

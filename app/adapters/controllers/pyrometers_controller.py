from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.domain.constants.pyrometer_constants import (
    COLOR_PATTERN,
    NICKNAME_MAX_LENGTH,
    NOTE_MAX_LENGTH,
)
from core.domain.errors.color_in_use_error import ColorInUseError
from core.domain.errors.pyrometer_not_found_error import PyrometerNotFoundError
from interfaces.core.application.i_list_pyrometer_summaries_use_case import (
    IListPyrometerSummariesUseCase,
)
from interfaces.core.application.i_list_pyrometers_use_case import IListPyrometersUseCase
from interfaces.core.application.i_save_pyrometer_profile_use_case import (
    ISavePyrometerProfileUseCase,
)


class PyrometerResponse(BaseModel):
    id: str
    name: str | None
    nickname: str | None
    color: str
    note: str | None
    active: bool


class PyrometerProfileRequest(BaseModel):
    """O complemento inteiro: o que nao vier volta ao padrao (sem apelido, cor padrao, ativo)."""

    nickname: str | None = Field(default=None, max_length=NICKNAME_MAX_LENGTH)
    color: str | None = Field(default=None, pattern=COLOR_PATTERN)
    note: str | None = Field(default=None, max_length=NOTE_MAX_LENGTH)
    active: bool = True


class PyrometerSummaryResponse(BaseModel):
    pyrometer_id: str
    temperature: int
    measured_at: datetime
    battery: int | None
    minutes_without_reading: int


class PyrometersController:
    """Lista, resume e complementa os pirometros. Nunca cria um: so existe o que esta nos dados."""

    def __init__(
        self,
        list_pyrometers_use_case: IListPyrometersUseCase,
        list_pyrometer_summaries_use_case: IListPyrometerSummariesUseCase,
        save_pyrometer_profile_use_case: ISavePyrometerProfileUseCase,
    ) -> None:
        self._list_pyrometers_use_case = list_pyrometers_use_case
        self._list_pyrometer_summaries_use_case = list_pyrometer_summaries_use_case
        self._save_pyrometer_profile_use_case = save_pyrometer_profile_use_case
        self.router = APIRouter(tags=["pirometros"])
        self.router.add_api_route(
            "/pyrometers",
            self.list_pyrometers,
            methods=["GET"],
            response_model=list[PyrometerResponse],
            summary="Pirometros existentes, com o complemento",
        )
        self.router.add_api_route(
            "/pyrometers/summary",
            self.list_summaries,
            methods=["GET"],
            response_model=list[PyrometerSummaryResponse],
            summary="Ultima leitura com temperatura de cada pirometro e ha quantos minutos",
        )
        self.router.add_api_route(
            "/pyrometers/{pyrometer_id}",
            self.save_pyrometer,
            methods=["PUT"],
            response_model=PyrometerResponse,
            summary="Grava o complemento de um pirometro existente",
        )

    def list_pyrometers(self) -> list[PyrometerResponse]:
        return [
            PyrometerResponse(
                id=item.id,
                name=item.name,
                nickname=item.nickname,
                color=item.color,
                note=item.note,
                active=item.active,
            )
            for item in self._list_pyrometers_use_case.execute()
        ]

    def list_summaries(self) -> list[PyrometerSummaryResponse]:
        return [
            PyrometerSummaryResponse(
                pyrometer_id=item.pyrometer_id,
                temperature=item.temperature,
                measured_at=item.measured_at,
                battery=item.battery,
                minutes_without_reading=item.minutes_without_reading,
            )
            for item in self._list_pyrometer_summaries_use_case.execute()
        ]

    def save_pyrometer(
        self, pyrometer_id: str, profile: PyrometerProfileRequest
    ) -> PyrometerResponse:
        try:
            self._save_pyrometer_profile_use_case.execute(
                pyrometer_id, profile.nickname, profile.color, profile.note, profile.active
            )
        except PyrometerNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ColorInUseError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        saved = next(
            item for item in self._list_pyrometers_use_case.execute() if item.id == pyrometer_id
        )
        return PyrometerResponse(
            id=saved.id,
            name=saved.name,
            nickname=saved.nickname,
            color=saved.color,
            note=saved.note,
            active=saved.active,
        )

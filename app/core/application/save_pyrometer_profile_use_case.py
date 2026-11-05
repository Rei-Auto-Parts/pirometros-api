from __future__ import annotations

from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto
from core.domain.errors.color_in_use_error import ColorInUseError
from core.domain.errors.pyrometer_not_found_error import PyrometerNotFoundError
from core.domain.models.pyrometer_overview_model import build_overviews
from interfaces.adapters.repositories.i_pyrometer_profile_repository import (
    IPyrometerProfileRepository,
)
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository


class SavePyrometerProfileUseCase:
    """So complementa pirometro que ja existe nos dados: nunca cria um novo nem repete cor."""

    def __init__(
        self,
        reading_repository: IReadingRepository,
        profile_repository: IPyrometerProfileRepository,
    ) -> None:
        self._reading_repository = reading_repository
        self._profile_repository = profile_repository

    def execute(
        self,
        pyrometer_id: str,
        nickname: str | None,
        color: str | None,
        note: str | None,
        active: bool,
    ) -> None:
        if not self._reading_repository.pyrometer_exists(pyrometer_id):
            raise PyrometerNotFoundError(pyrometer_id)
        if color is not None:
            self._ensure_color_is_free(pyrometer_id, color)
        self._profile_repository.save(
            PyrometerProfileDto(
                pyrometer_id, _blank_to_none(nickname), color, _blank_to_none(note), active
            )
        )

    def _ensure_color_is_free(self, pyrometer_id: str, color: str) -> None:
        overviews = build_overviews(
            self._reading_repository.find_pyrometers(), self._profile_repository.find_all()
        )
        used = {item.color.lower() for item in overviews if item.id != pyrometer_id}
        if color.lower() in used:
            raise ColorInUseError(color)


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None

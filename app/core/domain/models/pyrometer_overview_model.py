from __future__ import annotations

from collections.abc import Sequence

from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.pyrometer_overview_dto import PyrometerOverviewDto
from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto
from core.domain.models.default_color_model import assign_default_colors


def build_overviews(
    pyrometers: Sequence[PyrometerDto], profiles: Sequence[PyrometerProfileDto]
) -> list[PyrometerOverviewDto]:
    """Pirometros por serial, com o complemento e os padroes aplicados.

    A cor padrao so vai para quem nao escolheu cor, e nunca repete uma cor escolhida.
    """
    ordered = sorted(pyrometers, key=lambda item: item.id)
    by_id = {item.pyrometer_id: item for item in profiles}
    chosen: dict[str, str] = {}
    for item in ordered:
        profile = by_id.get(item.id)
        if profile is not None and profile.color:
            chosen[item.id] = profile.color
    without_color = [item.id for item in ordered if item.id not in chosen]
    default_colors = assign_default_colors(without_color, reserved_colors=list(chosen.values()))
    overviews: list[PyrometerOverviewDto] = []
    for pyrometer in ordered:
        profile = by_id.get(pyrometer.id)
        overviews.append(
            PyrometerOverviewDto(
                id=pyrometer.id,
                name=pyrometer.name,
                nickname=profile.nickname if profile else None,
                color=chosen.get(pyrometer.id) or default_colors[pyrometer.id],
                note=profile.note if profile else None,
                active=profile.active if profile else True,
            )
        )
    return overviews

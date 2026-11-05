from __future__ import annotations

import zlib
from collections.abc import Collection, Sequence

from core.domain.constants.pyrometer_constants import PALETTE


def assign_default_colors(
    pyrometer_ids: Sequence[str], reserved_colors: Collection[str] = ()
) -> dict[str, str]:
    """Cor padrao de cada serial: a mesma sempre, e diferente entre eles enquanto a paleta der.

    A cor preferida vem do hash do serial. Em colisao, o serial de ordem maior avanca para a
    proxima cor livre. Cores `reserved_colors` (escolhidas por alguem) nunca sao usadas. Passou da
    paleta, as cores se repetem.
    """
    palette = [color.lower() for color in PALETTE]
    taken: set[int] = {
        palette.index(color.lower()) for color in reserved_colors if color.lower() in palette
    }
    colors: dict[str, str] = {}
    for pyrometer_id in sorted(pyrometer_ids):
        preferred = zlib.crc32(pyrometer_id.encode()) % len(PALETTE)
        index = _first_free(preferred, taken)
        taken.add(index)
        colors[pyrometer_id] = PALETTE[index]
    return colors


def _first_free(preferred: int, taken: set[int]) -> int:
    for offset in range(len(PALETTE)):
        candidate = (preferred + offset) % len(PALETTE)
        if candidate not in taken:
            return candidate
    return preferred

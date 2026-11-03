from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from core.domain.dtos.readings_page_dto import ReadingsPageDto


class IListReadingsUseCase(Protocol):
    def execute(
        self,
        start: datetime,
        end: datetime,
        pyrometer_ids: Sequence[str],
        page: int,
        page_size: int,
    ) -> ReadingsPageDto:
        """Pagina de medicoes do periodo, da mais recente para a mais antiga."""
        ...

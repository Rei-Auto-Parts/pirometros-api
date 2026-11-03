from __future__ import annotations

from dataclasses import dataclass

from core.domain.dtos.reading_dto import ReadingDto


@dataclass(frozen=True)
class ReadingsPageDto:
    items: tuple[ReadingDto, ...]
    total: int
    page: int
    page_size: int

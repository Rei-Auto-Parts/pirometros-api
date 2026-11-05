from __future__ import annotations

from sqlalchemy import Engine, text

from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto

SELECT_ALL = text(
    "SELECT pyrometer_id, nickname, color, note, active FROM app.pyrometer_profile "
    "ORDER BY pyrometer_id"
)
UPSERT = text(
    "INSERT INTO app.pyrometer_profile (pyrometer_id, nickname, color, note, active) "
    "VALUES (:pyrometer_id, :nickname, :color, :note, :active) "
    "ON CONFLICT (pyrometer_id) DO UPDATE SET nickname = EXCLUDED.nickname, "
    "color = EXCLUDED.color, note = EXCLUDED.note, active = EXCLUDED.active, "
    "updated_at = now()"
)


class PyrometerProfileRepository:
    """Unica escrita da API: o complemento dos pirometros, so no schema `app`."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def find_all(self) -> list[PyrometerProfileDto]:
        with self._engine.connect() as connection:
            rows = connection.execute(SELECT_ALL).mappings().all()
        return [
            PyrometerProfileDto(
                pyrometer_id=row["pyrometer_id"],
                nickname=row["nickname"],
                color=row["color"],
                note=row["note"],
                active=row["active"],
            )
            for row in rows
        ]

    def save(self, profile: PyrometerProfileDto) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                UPSERT,
                {
                    "pyrometer_id": profile.pyrometer_id,
                    "nickname": profile.nickname,
                    "color": profile.color,
                    "note": profile.note,
                    "active": profile.active,
                },
            )

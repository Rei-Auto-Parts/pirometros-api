"""cria app.pyrometer_profile, o complemento dos pirometros

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-05
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sem chave estrangeira para `public.receiver_data`: a tabela e do sincronizador.
    op.execute("""
        CREATE TABLE IF NOT EXISTS app.pyrometer_profile (
            pyrometer_id varchar(14) PRIMARY KEY,
            nickname     varchar(40),
            color        varchar(7),
            note         varchar(500),
            active       boolean NOT NULL DEFAULT true,
            updated_at   timestamptz NOT NULL DEFAULT now()
        )
        """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS app.pyrometer_profile")

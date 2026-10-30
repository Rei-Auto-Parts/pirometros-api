"""cria o schema app

Revision ID: 0001
Revises:
Create Date: 2026-10-30
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS app")


def downgrade() -> None:
    # O schema `app` nunca e removido automaticamente: a tabela de versao mora nele.
    pass

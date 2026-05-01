"""add_is_demo_user_column

Revision ID: 20260501_add_is_demo_user
Revises: 20260430_123045
Create Date: 2026-05-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260501_add_is_demo_user"
down_revision: Union[str, Sequence[str], None] = "20260430_123045"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_demo_user", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "is_demo_user")

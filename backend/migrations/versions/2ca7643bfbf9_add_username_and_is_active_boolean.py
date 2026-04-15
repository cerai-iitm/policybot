"""add_username_and_is_active_boolean

Revision ID: 2ca7643bfbf9
Revises: 1b409ce7db8b
Create Date: 2026-04-13 21:24:25.526120

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2ca7643bfbf9"
down_revision: Union[str, Sequence[str], None] = "1b409ce7db8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=150), nullable=True))
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.add_column(
        "users",
        sa.Column(
            "is_active_bool", sa.Boolean(), server_default="true", nullable=False
        ),
    )

    op.execute(
        "UPDATE users SET is_active_bool = CASE WHEN lower(is_active) IN ('true', '1', 'yes') THEN true ELSE false END"
    )

    op.drop_column("users", "is_active")
    op.alter_column("users", "is_active_bool", new_column_name="is_active")
    op.alter_column("users", "username", nullable=False)


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.String(), server_default="true", nullable=True),
    )
    op.execute(
        "UPDATE users SET is_active = CASE WHEN is_active = true THEN 'true' ELSE 'false' END"
    )
    op.drop_column("users", "is_active_bool")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")

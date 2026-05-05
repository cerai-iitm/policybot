"""add_source_chunks_to_chat_messages

Revision ID: 20260503_add_source_chunks
Revises: 20260501_add_is_demo_user
Create Date: 2026-05-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260503_add_source_chunks"
down_revision: Union[str, Sequence[str], None] = "20260501_add_is_demo_user"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_messages",
        sa.Column("source_chunks", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chat_messages", "source_chunks")

"""create_chat_sessions_table

Revision ID: 20260430_123045
Revises: 20260418_202730
Create Date: 2026-04-30 12:30:45

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260430_123045"
down_revision: Union[str, Sequence[str], None] = "20260418_202730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(50), nullable=False),
        sa.Column("notebook_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["notebook_id"],
            ["notebooks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )

    op.create_index(
        "ix_chat_sessions_id",
        "chat_sessions",
        ["id"],
    )
    op.create_index(
        "ix_chat_sessions_session_id",
        "chat_sessions",
        ["session_id"],
    )
    op.create_index(
        "ix_chat_sessions_notebook_id",
        "chat_sessions",
        ["notebook_id"],
    )
    op.create_index(
        "ix_chat_sessions_user_id",
        "chat_sessions",
        ["user_id"],
    )

    op.drop_column("chat_messages", "session_id")

    op.add_column(
        "chat_messages",
        sa.Column("session_id", sa.Integer(), nullable=False),
    )

    op.create_foreign_key(
        "fk_chat_messages_session_id",
        "chat_messages",
        "chat_sessions",
        ["session_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_chat_messages_session_id",
        "chat_messages",
        type_="foreignkey",
    )

    op.drop_column("chat_messages", "session_id")

    op.add_column(
        "chat_messages",
        sa.Column("session_id", sa.String(100), nullable=False),
    )

    op.drop_index(
        "ix_chat_sessions_user_id",
        table_name="chat_sessions",
    )
    op.drop_index(
        "ix_chat_sessions_notebook_id",
        table_name="chat_sessions",
    )
    op.drop_index(
        "ix_chat_sessions_session_id",
        table_name="chat_sessions",
    )
    op.drop_index(
        "ix_chat_sessions_id",
        table_name="chat_sessions",
    )

    op.drop_table("chat_sessions")

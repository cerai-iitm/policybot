"""Initial tables migration

Revision ID: 1b409ce7db8b
Revises: None
Create Date: 2026-04-12 12:05:39.638070
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = "1b409ce7db8b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all core tables in the correct order.
    The `users` table must exist before any foreign‑key references to it.
    """
    # ---- users ----
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.String(), server_default="true"),
    )

    # ---- notebooks ----
    op.create_table(
        "notebooks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notebook_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_notebooks_id"), "notebooks", ["id"], unique=False)
    op.create_index(op.f("ix_notebooks_notebook_id"), "notebooks", ["notebook_id"], unique=True)

    # ---- chat_messages ----
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notebook_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["notebook_id"], ["notebooks.id"]),
    )
    op.create_index(op.f("ix_chat_messages_id"), "chat_messages", ["id"], unique=False)
    op.create_index(op.f("ix_chat_messages_session_id"), "chat_messages", ["session_id"], unique=False)

    # ---- pdfs ----
    op.create_table(
        "pdfs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notebook_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=36), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("processing_status", sa.String(length=50), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["notebook_id"], ["notebooks.id"]),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index(op.f("ix_pdfs_id"), "pdfs", ["id"], unique=False)


def downgrade() -> None:
    """Drop tables in reverse order of creation."""
    op.drop_index(op.f("ix_pdfs_id"), table_name="pdfs")
    op.drop_table("pdfs")
    op.drop_index(op.f("ix_chat_messages_session_id"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_id"), table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index(op.f("ix_notebooks_notebook_id"), table_name="notebooks")
    op.drop_index(op.f("ix_notebooks_id"), table_name="notebooks")
    op.drop_table("notebooks")
    op.drop_table("users")

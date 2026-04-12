"""Create suggested_questions table

Revision ID: 8f7a3d1e2b5c
Revises: f2ba32b9cace
Create Date: 2026-02-16 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f7a3d1e2b5c"
down_revision: Union[str, Sequence[str], None] = "f2ba32b9cace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "suggested_questions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("notebook_id", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_suggested_questions_notebook_id"),
        "suggested_questions",
        ["notebook_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_suggested_questions_filename"),
        "suggested_questions",
        ["filename"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_suggested_questions_filename"), table_name="suggested_questions"
    )
    op.drop_index(
        op.f("ix_suggested_questions_notebook_id"), table_name="suggested_questions"
    )
    op.drop_table("suggested_questions")

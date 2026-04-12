"""Create suggested_question_examples table

Revision ID: 1a2b3c4d5e6f
Revises: 8f7a3d1e2b5c
Create Date: 2026-02-17 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, Sequence[str], None] = "8f7a3d1e2b5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "suggested_question_examples",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("suggested_question_id", sa.String(), nullable=False),
        sa.Column("example_answer", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["suggested_question_id"],
            ["suggested_questions.id"],
            name=op.f("fk_suggested_question_examples_suggested_question_id"),
        ),
    )
    op.create_index(
        op.f("ix_suggested_question_examples_suggested_question_id"),
        "suggested_question_examples",
        ["suggested_question_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_suggested_question_examples_suggested_question_id"),
        table_name="suggested_question_examples",
    )
    op.drop_table("suggested_question_examples")

"""create_pdf_suggested_queries_table

Revision ID: 20260418_195344
Revises: 2ca7643bfbf9
Create Date: 2026-04-18 19:53:44

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = "20260418_195344"
down_revision: Union[str, Sequence[str], None] = "2ca7643bfbf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pdf_suggested_queries table
    op.create_table(
        "pdf_suggested_queries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pdf_id", sa.Integer(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["pdf_id"],
            ["pdfs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        "ix_pdf_suggested_queries_id",
        "pdf_suggested_queries",
        ["id"],
    )
    op.create_index(
        "ix_pdf_suggested_queries_pdf_id",
        "pdf_suggested_queries",
        ["pdf_id"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        "ix_pdf_suggested_queries_pdf_id",
        table_name="pdf_suggested_queries",
    )
    op.drop_index(
        "ix_pdf_suggested_queries_id",
        table_name="pdf_suggested_queries",
    )

    # Drop table
    op.drop_table("pdf_suggested_queries")

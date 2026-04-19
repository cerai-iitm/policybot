"""add_index_to_pdf_stored_filename

Revision ID: 20260418_202730
Revises: 20260418_195344
Create Date: 2026-04-18 20:27:30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = "20260418_202730"
down_revision: Union[str, Sequence[str], None] = "20260418_195344"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create index on stored_filename
    op.create_index(
        "ix_pdfs_stored_filename",
        "pdfs",
        ["stored_filename"],
    )


def downgrade() -> None:
    # Drop index
    op.drop_index("ix_pdfs_stored_filename", table_name="pdfs")

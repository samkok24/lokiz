"""rename_remix_count_to_glitch_count

Revision ID: 450377ba8eb0
Revises: 4b08818d25fe
Create Date: 2025-10-30 03:42:19.299426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '450377ba8eb0'
down_revision: Union[str, Sequence[str], None] = '4b08818d25fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename column while preserving data
    op.alter_column('videos', 'remix_count', new_column_name='glitch_count')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename column back
    op.alter_column('videos', 'glitch_count', new_column_name='remix_count')

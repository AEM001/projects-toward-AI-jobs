"""Create initial tables

Revision ID: de9091330829
Revises: d68cd9c525be
Create Date: 2026-02-21 17:58:13.671679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de9091330829'
down_revision: Union[str, Sequence[str], None] = 'd68cd9c525be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

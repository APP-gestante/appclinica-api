"""merge_heads_for_evolution

Revision ID: e4238327f236
Revises: e1f2a3b4c5d6, f1a2b3c4d5e6
Create Date: 2026-05-29 03:37:33.379457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4238327f236'
down_revision: Union[str, None] = ('e1f2a3b4c5d6', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

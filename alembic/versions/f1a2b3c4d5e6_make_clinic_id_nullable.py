"""make clinic_id nullable for superadmin

Revision ID: f1a2b3c4d5e6
Revises: 1b924d7ba5e3, a1b2c3d4e5f6
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, tuple] = ('1b924d7ba5e3', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'clinic_id', nullable=True)


def downgrade() -> None:
    op.alter_column('users', 'clinic_id', nullable=False)

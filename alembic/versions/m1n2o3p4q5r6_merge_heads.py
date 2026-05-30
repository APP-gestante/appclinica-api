"""merge heads

Revision ID: m1n2o3p4q5r6
Revises: 917cfc2cf59c, g7h8i9j0k1l2
Create Date: 2026-05-29
"""
from alembic import op
from typing import Union

revision = 'm1n2o3p4q5r6'
down_revision: Union[tuple, None] = ('917cfc2cf59c', 'g7h8i9j0k1l2')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""add superadmin role

Revision ID: cdbf52e8db96
Revises: 997121b7f6fb
Create Date: 2026-05-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdbf52e8db96'
down_revision: Union[str, None] = '997121b7f6fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL does not allow ALTER TYPE ... ADD VALUE to run inside a transaction block
    # We use op.execute with autocommit or similar approach.
    # For simplicity in this environment, we use a raw SQL execution.
    # Note: 'userrole' is the name of the enum in the database as seen in migration 997121b7f6fb
    op.execute("ALTER TYPE userrole ADD VALUE 'superadmin'")


def downgrade() -> None:
    # Removing a value from an ENUM is not directly supported by PostgreSQL.
    # It usually requires creating a new type, moving data, and dropping the old one.
    # Given this is a new feature addition, we leave it as a no-op or a warning.
    pass

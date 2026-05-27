"""add announcements table

Revision ID: a1b2c3d4e5f6
Revises: cdbf52e8db96
Create Date: 2026-05-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cdbf52e8db96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

announcement_category = postgresql.ENUM(
    'agenda', 'saude', 'clinica', 'geral',
    name='announcementcategory',
    create_type=False,
)


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE announcementcategory AS ENUM ('agenda', 'saude', 'clinica', 'geral');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.create_table(
        'announcements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', announcement_category, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('short_description', sa.String(500), nullable=False),
        sa.Column('full_description', sa.Text, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_announcements_clinic_id', 'announcements', ['clinic_id'])
    op.create_index('ix_announcements_category', 'announcements', ['category'])


def downgrade() -> None:
    op.drop_index('ix_announcements_category', table_name='announcements')
    op.drop_index('ix_announcements_clinic_id', table_name='announcements')
    op.drop_table('announcements')
    op.execute("DROP TYPE IF EXISTS announcementcategory")

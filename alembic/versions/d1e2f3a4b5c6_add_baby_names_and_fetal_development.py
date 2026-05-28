"""add baby_names and fetal_development tables

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
Create Date: 2026-05-27 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

baby_name_gender = postgresql.ENUM('male', 'female', 'neutral', name='babynamegender', create_type=False)
name_trend = postgresql.ENUM('rising', 'stable', 'declining', name='nametrend', create_type=False)


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE babynamegender AS ENUM ('male', 'female', 'neutral');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE nametrend AS ENUM ('rising', 'stable', 'declining');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)

    op.create_table(
        'baby_names',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('gender', baby_name_gender, nullable=False),
        sa.Column('origin', sa.String(100), nullable=True),
        sa.Column('meaning', sa.Text, nullable=True),
        sa.Column('popularity_score', sa.SmallInteger, nullable=True),
        sa.Column('trend', name_trend, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_baby_names_name', 'baby_names', ['name'])
    op.create_index('ix_baby_names_gender', 'baby_names', ['gender'])

    op.create_table(
        'patient_baby_name_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('baby_name_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('baby_names.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('patient_id', 'baby_name_id', name='uq_patient_baby_name'),
    )
    op.create_index('ix_patient_baby_name_favorites_patient_id', 'patient_baby_name_favorites', ['patient_id'])

    op.create_table(
        'fetal_development',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('week', sa.SmallInteger, nullable=False, unique=True),
        sa.Column('size_cm', sa.Numeric(5, 2), nullable=True),
        sa.Column('weight_g', sa.Numeric(7, 2), nullable=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('highlights', postgresql.JSON, nullable=True),
        sa.Column('image_url', sa.Text, nullable=True),
        sa.Column('model_url', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_fetal_development_week', 'fetal_development', ['week'])


def downgrade() -> None:
    op.drop_index('ix_fetal_development_week', table_name='fetal_development')
    op.drop_table('fetal_development')

    op.drop_index('ix_patient_baby_name_favorites_patient_id', table_name='patient_baby_name_favorites')
    op.drop_table('patient_baby_name_favorites')

    op.drop_index('ix_baby_names_gender', table_name='baby_names')
    op.drop_index('ix_baby_names_name', table_name='baby_names')
    op.drop_table('baby_names')

    op.execute("DROP TYPE IF EXISTS nametrend")
    op.execute("DROP TYPE IF EXISTS babynamegender")

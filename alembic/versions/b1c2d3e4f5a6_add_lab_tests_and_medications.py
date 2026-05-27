"""add lab_tests and medications tables

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-05-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

lab_test_type = postgresql.ENUM('hemograma', 'glicemia', 'urina', 'outros', name='labtesttype', create_type=False)
lab_test_status = postgresql.ENUM('pending', 'completed', 'abnormal', name='labteststatus', create_type=False)


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE labtesttype AS ENUM ('hemograma', 'glicemia', 'urina', 'outros');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE labteststatus AS ENUM ('pending', 'completed', 'abnormal');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)

    op.create_table(
        'lab_tests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('type', lab_test_type, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('result', sa.Text, nullable=True),
        sa.Column('reference_range', sa.String(255), nullable=True),
        sa.Column('status', lab_test_status, nullable=False, server_default='pending'),
        sa.Column('file_url', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_lab_tests_patient_id', 'lab_tests', ['patient_id'])
    op.create_index('ix_lab_tests_date', 'lab_tests', ['date'])

    op.create_table(
        'medications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('dosage', sa.String(100), nullable=False),
        sa.Column('frequency', sa.String(100), nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('instructions', sa.Text, nullable=True),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_medications_patient_id', 'medications', ['patient_id'])
    op.create_index('ix_medications_active', 'medications', ['active'])

    op.add_column('users', sa.Column('push_token', sa.String(512), nullable=True))
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean, nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'onboarding_completed')
    op.drop_column('users', 'push_token')

    op.drop_index('ix_medications_active', table_name='medications')
    op.drop_index('ix_medications_patient_id', table_name='medications')
    op.drop_table('medications')

    op.drop_index('ix_lab_tests_date', table_name='lab_tests')
    op.drop_index('ix_lab_tests_patient_id', table_name='lab_tests')
    op.drop_table('lab_tests')

    op.execute("DROP TYPE IF EXISTS labteststatus")
    op.execute("DROP TYPE IF EXISTS labtesttype")

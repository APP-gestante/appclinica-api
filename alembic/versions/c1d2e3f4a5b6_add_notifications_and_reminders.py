"""add notifications and reminders tables

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-05-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

notification_type = postgresql.ENUM(
    'appointment_reminder', 'clinic_announcement', 'vital_alert',
    name='notificationtype', create_type=False,
)
reminder_type = postgresql.ENUM(
    'appointment', 'exam', 'medication',
    name='remindertype', create_type=False,
)


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationtype AS ENUM ('appointment_reminder', 'clinic_announcement', 'vital_alert');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE remindertype AS ENUM ('appointment', 'exam', 'medication');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)

    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', notification_type, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('data', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_read', 'notifications', ['read'])

    op.create_table(
        'reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('type', reminder_type, nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('send_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_reminders_patient_id', 'reminders', ['patient_id'])
    op.create_index('ix_reminders_send_at', 'reminders', ['send_at'])


def downgrade() -> None:
    op.drop_index('ix_reminders_send_at', table_name='reminders')
    op.drop_index('ix_reminders_patient_id', table_name='reminders')
    op.drop_table('reminders')

    op.drop_index('ix_notifications_read', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')

    op.execute("DROP TYPE IF EXISTS remindertype")
    op.execute("DROP TYPE IF EXISTS notificationtype")

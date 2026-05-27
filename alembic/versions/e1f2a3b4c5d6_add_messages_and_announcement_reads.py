"""add messages and user_announcement_reads tables

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-05-27 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

message_sender_type = postgresql.ENUM(
    'patient', 'doctor', 'secretary', 'system',
    name='messagesendertype', create_type=False,
)


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE messagesendertype AS ENUM ('patient', 'doctor', 'secretary', 'system');
        EXCEPTION WHEN duplicate_object THEN null; END $$;
    """)

    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('sender_role', message_sender_type, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_messages_patient_id', 'messages', ['patient_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    op.create_table(
        'user_announcement_reads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('announcement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('announcements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('user_id', 'announcement_id', name='uq_user_announcement_read'),
    )
    op.create_index('ix_user_announcement_reads_user_id', 'user_announcement_reads', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_announcement_reads_user_id', table_name='user_announcement_reads')
    op.drop_table('user_announcement_reads')

    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_patient_id', table_name='messages')
    op.drop_table('messages')

    op.execute("DROP TYPE IF EXISTS messagesendertype")

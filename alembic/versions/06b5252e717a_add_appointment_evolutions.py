"""add_appointment_evolutions

Revision ID: 06b5252e717a
Revises: e4238327f236
Create Date: 2026-05-29 03:37:48.191513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '06b5252e717a'
down_revision: Union[str, None] = 'e4238327f236'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'appointment_evolutions',
        sa.Column('appointment_id', sa.UUID(), nullable=False),
        sa.Column('patient_id', sa.UUID(), nullable=False),
        sa.Column('weight_kg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('fundal_height_cm', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('fetal_heart_rate', sa.SmallInteger(), nullable=True),
        sa.Column('presentation', postgresql.ENUM('cephalic', 'breech', 'transverse',
                  name='fetalpresentation', create_type=False), nullable=True),
        sa.Column('fetal_movements', sa.Boolean(), nullable=True),
        sa.Column('edema', sa.String(length=5), nullable=True),
        sa.Column('bp_systolic', sa.SmallInteger(), nullable=True),
        sa.Column('bp_diastolic', sa.SmallInteger(), nullable=True),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appointment_id'),
    )


def downgrade() -> None:
    op.drop_table('appointment_evolutions')

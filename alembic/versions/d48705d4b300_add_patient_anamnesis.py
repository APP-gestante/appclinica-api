"""add_patient_anamnesis

Revision ID: d48705d4b300
Revises: 06b5252e717a
Create Date: 2026-05-29 04:20:21.530189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd48705d4b300'
down_revision: Union[str, None] = '06b5252e717a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'patient_anamnesis',
        sa.Column('patient_id', sa.UUID(), nullable=False),
        sa.Column('has_diabetes', sa.Boolean(), nullable=False),
        sa.Column('has_hipertensao', sa.Boolean(), nullable=False),
        sa.Column('has_cardiopatia', sa.Boolean(), nullable=False),
        sa.Column('has_epilepsia', sa.Boolean(), nullable=False),
        sa.Column('has_tireoide', sa.Boolean(), nullable=False),
        sa.Column('has_doenca_renal', sa.Boolean(), nullable=False),
        sa.Column('has_autoimune', sa.Boolean(), nullable=False),
        sa.Column('outras_doencas', sa.Text(), nullable=True),
        sa.Column('alergias_medicamentos', sa.Text(), nullable=True),
        sa.Column('outras_alergias', sa.Text(), nullable=True),
        sa.Column('familiar_diabetes', sa.Boolean(), nullable=False),
        sa.Column('familiar_hipertensao', sa.Boolean(), nullable=False),
        sa.Column('familiar_gemelaridade', sa.Boolean(), nullable=False),
        sa.Column('familiar_malformacoes', sa.Boolean(), nullable=False),
        sa.Column('outros_familiares', sa.Text(), nullable=True),
        sa.Column('tabagismo', sa.Boolean(), nullable=False),
        sa.Column('tabagismo_cigarros_dia', sa.SmallInteger(), nullable=True),
        sa.Column('alcool', sa.Boolean(), nullable=False),
        sa.Column('alcool_frequencia', sa.String(length=20), nullable=True),
        sa.Column('drogas_ilicitas', sa.Boolean(), nullable=False),
        sa.Column('atividade_fisica', sa.Boolean(), nullable=False),
        sa.Column('atividade_fisica_descricao', sa.String(length=255), nullable=True),
        sa.Column('pre_eclampsia_anterior', sa.Boolean(), nullable=False),
        sa.Column('diabetes_gestacional_anterior', sa.Boolean(), nullable=False),
        sa.Column('perda_fetal_anterior', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('patient_id'),
    )


def downgrade() -> None:
    op.drop_table('patient_anamnesis')

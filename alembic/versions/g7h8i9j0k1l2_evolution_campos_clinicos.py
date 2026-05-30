"""evolution: add queixas, obs_medicas, pfe, doppler, obs_exame_fisico, conduta

Revision ID: g7h8i9j0k1l2
Revises: e4238327f236
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = 'g7h8i9j0k1l2'
down_revision = 'e4238327f236'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('appointment_evolutions', sa.Column('queixas', sa.Text(), nullable=True))
    op.add_column('appointment_evolutions', sa.Column('observacoes_medicas', sa.Text(), nullable=True))
    op.add_column('appointment_evolutions', sa.Column('pfe_gramas', sa.SmallInteger(), nullable=True))
    op.add_column('appointment_evolutions', sa.Column('pfe_percentil', sa.String(10), nullable=True))
    op.add_column('appointment_evolutions', sa.Column('doppler', sa.String(50), nullable=True))
    op.add_column('appointment_evolutions', sa.Column('observacoes_exame_fisico', sa.Text(), nullable=True))
    op.add_column('appointment_evolutions', sa.Column('conduta', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('appointment_evolutions', 'conduta')
    op.drop_column('appointment_evolutions', 'observacoes_exame_fisico')
    op.drop_column('appointment_evolutions', 'doppler')
    op.drop_column('appointment_evolutions', 'pfe_percentil')
    op.drop_column('appointment_evolutions', 'pfe_gramas')
    op.drop_column('appointment_evolutions', 'observacoes_medicas')
    op.drop_column('appointment_evolutions', 'queixas')

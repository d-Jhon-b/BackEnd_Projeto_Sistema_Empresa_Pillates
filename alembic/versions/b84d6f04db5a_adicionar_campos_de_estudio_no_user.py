"""adicionar_campos_de_estudio_no_user

Revision ID: b84d6f04db5a
Revises: 1a9a41045822
Create Date: 2025-10-18 18:53:49.619699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b84d6f04db5a'
down_revision: Union[str, Sequence[str], None] = '1a9a41045822'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    estudio_aplicado_enum = sa.Enum('itaquera', 'são miguel', name='estudio_aplicado_enum')
    estudio_aplicado_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('usuario', sa.Column(
        'estudio_aplicado',
        estudio_aplicado_enum,
        nullable=True,
        server_default='itaquera'
    ))
    op.add_column('usuario', sa.Column('fk_id_estudio', sa.Integer, nullable=True))
    # op.add_column('usuario', sa.Column('fk_id_estudio', sa.Integer, server_default='1', nullable=True))

    op.create_foreign_key('fk_usuario_estudio_id','usuario','estudio',['fk_id_estudio'],['id_estudio'], ondelete='SET NULL')

    op.create_index(op.f('ix_usuario_fk_id_estudio'), 'usuario', ['fk_id_estudio'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f('ix_usuario_fk_id_estudio'), table_name='usuario')
    op.drop_constraint('fk_usuario_estudio_id', 'usuario', type_='foreignkey')
    op.drop_column('usuario', 'fk_id_estudio')
    op.drop_column('usuario', 'estudio_aplicado')
    op.execute('DROP TYPE estudio_aplicado_enum;')

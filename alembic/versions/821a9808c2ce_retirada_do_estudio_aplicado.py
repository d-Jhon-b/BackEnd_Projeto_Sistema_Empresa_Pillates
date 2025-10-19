"""retirada do estudio aplicado

Revision ID: 821a9808c2ce
Revises: 7b8f6ceec8f9
Create Date: 2025-10-18 20:46:52.634431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '821a9808c2ce'
down_revision: Union[str, Sequence[str], None] = '7b8f6ceec8f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('usuario', 'estudio_aplicado')
    op.execute('DROP TYPE IF EXISTS estudio_aplicado_enum;')


def downgrade() -> None:
    """Downgrade schema."""
    estudio_aplicado_enum = sa.Enum('itaquera', 'são miguel', name='estudio_aplicado_enum')
    estudio_aplicado_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('usuario', sa.Column(
        'estudio_aplicado',
        estudio_aplicado_enum,
        nullable=False,
        server_default='itaquera'
    ))

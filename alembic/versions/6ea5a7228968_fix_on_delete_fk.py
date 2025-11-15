"""fix_on_delete_fk

Revision ID: 6ea5a7228968
Revises: 821a9808c2ce
Create Date: 2025-11-02 21:00:16.566930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ea5a7228968'
down_revision: Union[str, Sequence[str], None] = '821a9808c2ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('fk_usuario_estudio_id', 'usuario', type_='foreignkey')

    # 2. Recriar a Foreign Key com ON DELETE SET NULL
    op.create_foreign_key(
        'fk_usuario_estudio_id',
        'usuario',
        'estudio',
        ['fk_id_estudio'],
        ['id_estudio'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_usuario_estudio_id', 'usuario', type_='foreignkey')

    # 2. Recriar a Foreign Key sem a cláusula ondelete
    op.create_foreign_key(
        'fk_usuario_estudio_id',
        'usuario',
        'estudio',
        ['fk_id_estudio'],
        ['id_estudio'],
        # Sem 'ondelete', o PostgreSQL usará o padrão (RESTRICT)
    )

"""create tabela usuarios

Revision ID: 7cfb67febedc
Revises: 
Create Date: 2025-09-23 20:08:10.391972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cfb67febedc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('senha', sa.String(200), nullable=False),
        sa.Column('idade', sa.Integer, nullable=False)

    )


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""create tabela usuarios

Revision ID: 30558ff058d5
Revises: 7cfb67febedc
Create Date: 2025-09-23 20:31:53.737073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30558ff058d5'
down_revision: Union[str, Sequence[str], None] = '7cfb67febedc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

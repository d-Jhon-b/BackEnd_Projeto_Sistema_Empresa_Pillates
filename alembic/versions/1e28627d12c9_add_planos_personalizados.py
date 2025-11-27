"""add_planos_personalizados

Revision ID: 1e28627d12c9
Revises: 6ea5a7228968
Create Date: 2025-11-15 15:27:35.988325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e28627d12c9'
down_revision: Union[str, Sequence[str], None] = '6ea5a7228968'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    planos = [
        ('mensal', '1x_semana', 'Plano mensal 1x por semana', 210.00, 4),
        ('mensal', '2x_semana', 'Plano mensal 2x por semana', 310.00, 8),
        ('mensal', '3x_semana', 'Plano mensal 3x por semana', 390.00, 12),

        ('trimestral', '1x_semana', 'Plano trimestral 1x por semana', 185.00, 12),
        ('trimestral', '2x_semana', 'Plano trimestral 2x por semana', 285.00, 24),
        ('trimestral', '3x_semana', 'Plano trimestral 3x por semana', 375.00, 36),

        ('semestral', '1x_semana', 'Plano semestral 1x por semana', 170.00, 24),
        ('semestral', '2x_semana', 'Plano semestral 2x por semana', 270.00, 48),
        ('semestral', '3x_semana', 'Plano semestral 3x por semana', 360.00, 72),

        ('anual', '1x_semana', 'Plano anual 1x por semana', 155.00, 48),
        ('anual', '2x_semana', 'Plano anual 2x por semana', 255.00, 96),
        ('anual', '3x_semana', 'Plano anual 3x por semana', 345.00, 144),
    ]

    for tipo, modalidade, desc, valor, aulas in planos:
        connection.execute(
            sa.text("""
                INSERT INTO planos (tipo_plano, modalidade_plano, descricao_plano, valor_plano, qtde_aulas_totais)
                VALUES (:tipo, :mod, :desc, :valor, :aulas)
            """),
            {"tipo": tipo, "mod": modalidade, "desc": desc, "valor": valor, "aulas": aulas}
        )




def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE solicitacoes
            SET fk_id_novo_plano = NULL
            WHERE fk_id_novo_plano IN (
                SELECT id_plano FROM planos
                WHERE tipo_plano IN ('mensal','trimestral','semestral','anual')
                AND modalidade_plano IN ('1x_semana','2x_semana','3x_semana')
            )
        """)
    )

    connection.execute(
        sa.text("""
            DELETE FROM planos
            WHERE tipo_plano IN ('mensal','trimestral','semestral','anual')
            AND modalidade_plano IN ('1x_semana','2x_semana','3x_semana')
        """)
    )
    # connection.execute(
    #     sa.text("""
    #         DELETE FROM planos
    #         WHERE tipo_plano IN ('mensal','trimestral','semestral','anual')
    #         AND modalidade_plano IN ('1x_semana','2x_semana','3x_semana')
    #     """)
      
    # )

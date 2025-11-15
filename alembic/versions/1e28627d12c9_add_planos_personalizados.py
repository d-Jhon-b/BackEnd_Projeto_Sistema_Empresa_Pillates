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
    pass
    # op.create_table(
    #     'planos_personalizados',
    #     sa.Column('id_plano_personalizado', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
    #     sa.Column('nome_plano', sa.String(255), nullable=False),
    #     sa.Column('tipo_plano_livre', sa.String(100), nullable=False), # String livre
    #     sa.Column('modalidade_plano_livre', sa.String(100), nullable=False), # String livre
        
    #     sa.Column('descricao_plano', sa.String(255), nullable=True),
    #     sa.Column('valor_plano', sa.Numeric(precision=10, scale=2), nullable=False),
    #     sa.Column('qtde_aulas_totais', sa.Integer, nullable=False),
    #     sa.Column('is_temporario', sa.Boolean, nullable=False, server_default=sa.text('false')),
    #     sa.Column('data_criacao', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    #     sa.Column('data_validade', sa.DateTime, nullable=True),
        
    #     # Mantendo as constraints de CHECK para valor e quantidade, mas com nome diferente
    #     sa.CheckConstraint('valor_plano <= 999.99', name='chk_valor_plano_personalizado_max'),
    #     sa.CheckConstraint('qtde_aulas_totais <= 1000', name='chk_aulas_totais_personalizado_max')
    # )

    # # 2. Adiciona a chave estrangeira na tabela 'contrato'
    # op.add_column(
    #     'contrato', 
    #     sa.Column(
    #         'fk_id_plano_personalizado', 
    #         sa.Integer, 
    #         sa.ForeignKey('planos_personalizados.id_plano_personalizado', ondelete='SET NULL'), 
    #         nullable=True
    #     )
    # )
    
    # # 3. Adiciona um CHECK CONSTRAINT para garantir que APENAS UM dos FKs de plano seja preenchido
    # # Isso é crucial para a integridade: um contrato ou usa um plano padrão, ou um plano personalizado.
    # op.create_check_constraint(
    #     'chk_one_plan_fk_active', 
    #     'contrato', 
    #     '(fk_id_plano IS NULL OR fk_id_plano_personalizado IS NULL)'
    # )


def downgrade() -> None:
    """Downgrade schema."""
    pass
    # op.drop_constraint('chk_one_plan_fk_active', 'contrato', type_='check')
    
    # # 2. Remove a coluna de chave estrangeira da tabela 'contrato'
    # op.drop_column('contrato', 'fk_id_plano_personalizado')
    
    # # 3. Remove a tabela 'planos_personalizados'
    # op.drop_table('planos_personalizados')

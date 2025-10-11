"""create_index_tables

Revision ID: 1a9a41045822
Revises: f479641b1064
Create Date: 2025-10-11 16:55:24.266644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a9a41045822'
down_revision: Union[str, Sequence[str], None] = 'f479641b1064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    """Adiciona índices nas colunas de Chave Estrangeira (FKs)."""
    
   
    # Tabelas de detalhes do Usuário (FKs para 'usuario.id_user')
   
    op.create_index(op.f('ix_endereco_fk_id_user'), 'endereco', ['fk_id_user'], unique=False)
    op.create_index(op.f('ix_email_fk_id_user'), 'email', ['fk_id_user'], unique=False)
    op.create_index(op.f('ix_contato_fk_id_user'), 'contato', ['fk_id_user'], unique=False)
    
   
    # Tabelas de Papéis (FKs para 'usuario.id_user')
   
    op.create_index(op.f('ix_estudante_fk_id_user'), 'estudante', ['fk_id_user'], unique=True) # Unique, pois a relação é 1:1 com 'usuario'
    op.create_index(op.f('ix_professor_fk_id_user'), 'professor', ['fk_id_user'], unique=True) # Unique, pois a relação é 1:1 com 'usuario'
    op.create_index(op.f('ix_administracao_fk_id_user'), 'administracao', ['fk_id_user'], unique=True) # Unique
    op.create_index(op.f('ix_recepcionista_fk_id_user'), 'recepcionista', ['fk_id_user'], unique=True) # Unique
    op.create_index(op.f('ix_adm_plus_fk_id_user'), 'adm_plus', ['fk_id_user'], unique=True) # Unique

   
    # Tabelas de Registro, Ligação e Adesão
   

    # Tabela 'registro_do_aluno' (FKs para 'estudante' e 'professor')
    op.create_index(op.f('ix_registro_aluno_fk_id_estudante'), 'registro_do_aluno', ['fk_id_estudante'], unique=False)
    op.create_index(op.f('ix_registro_aluno_fk_id_professor'), 'registro_do_aluno', ['fk_id_professor'], unique=False)
    
    # Tabela 'professor_estudante' (FKs para 'estudante' e 'professor')
    op.create_index(op.f('ix_prof_estudante_fk_id_estudante'), 'professor_estudante', ['fk_id_estudante'], unique=False)
    op.create_index(op.f('ix_prof_estudante_fk_id_professor'), 'professor_estudante', ['fk_id_professor'], unique=False)
    
    # Tabela 'adesao_plano' (FK para 'usuario')
    op.create_index(op.f('ix_adesao_plano_fk_id_user'), 'adesao_plano', ['fk_id_user'], unique=False)

   
    """Tabelas de Aulas"""

    # Tabela 'aula' (FKs para 'estudio' e 'professor')
    op.create_index(op.f('ix_aula_fk_id_estudio'), 'aula', ['fk_id_estudio'], unique=False)
    op.create_index(op.f('ix_aula_fk_id_professor'), 'aula', ['fk_id_professor'], unique=False)

    # Tabela 'estudante_aula' (FKs para 'estudante' e 'aula')
    op.create_index(op.f('ix_estudante_aula_fk_id_estudante'), 'estudante_aula', ['fk_id_estudante'], unique=False)
    op.create_index(op.f('ix_estudante_aula_fk_id_aula'), 'estudante_aula', ['fk_id_aula'], unique=False)
    
   
    # Tabelas Financeiras
   
    
    # Tabela 'contrato' (FKs para 'estudante' e 'planos')
    op.create_index(op.f('ix_contrato_fk_id_estudante'), 'contrato', ['fk_id_estudante'], unique=False)
    op.create_index(op.f('ix_contrato_fk_id_plano'), 'contrato', ['fk_id_plano'], unique=False)

    # Tabela 'venda_extra' (FK para 'estudante')
    op.create_index(op.f('ix_venda_extra_fk_id_estudante'), 'venda_extra', ['fk_id_estudante'], unique=False)
    
    # Tabela 'pagamento' (FKs para 'contrato', 'estudante' e 'venda_extra')
    op.create_index(op.f('ix_pagamento_fk_id_contrato'), 'pagamento', ['fk_id_contrato'], unique=False)
    op.create_index(op.f('ix_pagamento_fk_id_estudante'), 'pagamento', ['fk_id_estudante'], unique=False)
    op.create_index(op.f('ix_pagamento_fk_id_venda_extra'), 'pagamento', ['fk_id_venda_extra'], unique=False)




def downgrade() -> None:
    """Downgrade schema."""
    """Remove os índices criados."""

    # Remoção de Índices Financeiros
    op.drop_index(op.f('ix_pagamento_fk_id_venda_extra'), table_name='pagamento')
    op.drop_index(op.f('ix_pagamento_fk_id_estudante'), table_name='pagamento')
    op.drop_index(op.f('ix_pagamento_fk_id_contrato'), table_name='pagamento')
    
    op.drop_index(op.f('ix_venda_extra_fk_id_estudante'), table_name='venda_extra')

    op.drop_index(op.f('ix_contrato_fk_id_plano'), table_name='contrato')
    op.drop_index(op.f('ix_contrato_fk_id_estudante'), table_name='contrato')

    # Remoção de Índices de Aulas
    op.drop_index(op.f('ix_estudante_aula_fk_id_aula'), table_name='estudante_aula')
    op.drop_index(op.f('ix_estudante_aula_fk_id_estudante'), table_name='estudante_aula')

    op.drop_index(op.f('ix_aula_fk_id_professor'), table_name='aula')
    op.drop_index(op.f('ix_aula_fk_id_estudio'), table_name='aula')
    
    # Remoção de Índices de Registro, Ligação e Adesão
    op.drop_index(op.f('ix_adesao_plano_fk_id_user'), table_name='adesao_plano')

    op.drop_index(op.f('ix_prof_estudante_fk_id_professor'), table_name='professor_estudante')
    op.drop_index(op.f('ix_prof_estudante_fk_id_estudante'), table_name='professor_estudante')

    op.drop_index(op.f('ix_registro_aluno_fk_id_professor'), table_name='registro_do_aluno')
    op.drop_index(op.f('ix_registro_aluno_fk_id_estudante'), table_name='registro_do_aluno')

    # Remoção de Índices de Papéis
    op.drop_index(op.f('ix_adm_plus_fk_id_user'), table_name='adm_plus')
    op.drop_index(op.f('ix_recepcionista_fk_id_user'), table_name='recepcionista')
    op.drop_index(op.f('ix_administracao_fk_id_user'), table_name='administracao')
    op.drop_index(op.f('ix_professor_fk_id_user'), table_name='professor')
    op.drop_index(op.f('ix_estudante_fk_id_user'), table_name='estudante')

    # Remoção de Índices de detalhes do Usuário
    op.drop_index(op.f('ix_contato_fk_id_user'), table_name='contato')
    op.drop_index(op.f('ix_email_fk_id_user'), table_name='email')
    op.drop_index(op.f('ix_endereco_fk_id_user'), table_name='endereco')

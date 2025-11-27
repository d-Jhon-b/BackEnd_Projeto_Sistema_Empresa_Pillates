"""adicionar_dados_iniciais_de_estudios_(itaquera_e_são_miguel)

Revision ID: 7b8f6ceec8f9
Revises: b84d6f04db5a
Create Date: 2025-10-18 19:04:32.995062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b8f6ceec8f9'
down_revision: Union[str, Sequence[str], None] = 'b84d6f04db5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    estudio_table = sa.table('estudio',
        sa.column('id_estudio', sa.Integer),
        sa.column('endereco_estudio', sa.String),
        sa.column('cep_estudio', sa.String),
        sa.column('mongo_registros_estudio', sa.String)
    )

    op.bulk_insert(estudio_table,
        [
            {
                'id_estudio': 1,
                'endereco_estudio': 'Estr. Itaquera Guaianazes, 45 - Parada XV de Novembro, São Paulo - SP',
                'cep_estudio': '08246000',
                'mongo_registros_estudio': 'placeholder_itaquera'
            },
            {
                'id_estudio': 2,
                'endereco_estudio': 'Rua: José Aldo Piassi, 165 - São Miguel Paulista, São Paulo - SP ',
                'cep_estudio': '08011280',
                'mongo_registros_estudio': 'placeholder_sao_miguel'
            }
        ]
    )
    #email para uso: soraya@exemplo.com
    #senha a user: senhaForte123
    hashed_password = '$2b$05$AwcnFEHChDo7ccpvK6cui.KtOgPp4VpjsnvFNVbteFOyxg1lKQWfa'

    usuario_table = sa.table('usuario',
        sa.column('id_user', sa.Integer),
        sa.column('name_user', sa.String),
        sa.column('tipo_doc_user', sa.String),
        sa.column('num_doc_user', sa.String),
        sa.column('lv_acesso', sa.String),
        sa.column('tipo_email', sa.String),
        sa.column('email_user', sa.String),
        sa.column('senha_user', sa.String),
        sa.column('estudio_aplicado', sa.String),
        sa.column('fk_id_estudio', sa.Integer)
    )
    
    contato_table = sa.table('contato',
        sa.column('fk_id_user', sa.Integer),
        sa.column('tipo_contato', sa.String),
        sa.column('numero_contato', sa.String)
    )

    endereco_table = sa.table('endereco',
        sa.column('fk_id_user', sa.Integer),                          
        sa.column('tipo_endereco', sa.String),                         
        sa.column('endereco', sa.String),                          
        sa.column('cep', sa.String)                          
    )


    adm_plus_table = sa.table('adm_plus',
        sa.column('fk_id_user', sa.Integer)
    )

    op.bulk_insert(usuario_table,
        [
            {
                'id_user': 1,
                'name_user': 'Soraya',
                'tipo_doc_user': 'cpf',
                'num_doc_user': '00000000000', 
                'lv_acesso': 'supremo', 
                'tipo_email': 'pessoal',
                'email_user': 'soraya@exemplo.com',
                'senha_user': hashed_password,
                'estudio_aplicado': 'itaquera',
                'fk_id_estudio': 1 
            },
            {
                'id_user': 2,
                'name_user': 'adm_plus_2',
                'tipo_doc_user': 'cpf',
                'num_doc_user': '11111111111', 
                'lv_acesso': 'supremo',
                'tipo_email': 'comercial',
                'email_user': 'adm2@exemplo.com',
                'senha_user': hashed_password,
                'estudio_aplicado': 'são miguel',
                'fk_id_estudio': 2 
            }
        ]
    )

    op.bulk_insert(endereco_table,
        [
            {'fk_id_user': 1, 'tipo_endereco': 'comercial', 'endereco': 'R. adm1', 'cep': '03570450'},
            {'fk_id_user': 2, 'tipo_endereco': 'comercial', 'endereco': 'R. adm2', 'cep': '03570450'} # Valor temporário
        ]
    )
    op.bulk_insert(contato_table,
        [
            {'fk_id_user': 1, 'tipo_contato': 'comercial', 'numero_contato': '11970225137'},
            {'fk_id_user': 2, 'tipo_contato': 'comercial', 'numero_contato': '11999999999'} # Valor temporário
        ]
    )
    
    op.bulk_insert(adm_plus_table,
        [
            {'fk_id_user': 1},
            {'fk_id_user': 2}
        ]
    )
    op.execute(
        "SELECT setval('estudio_id_estudio_seq', (SELECT MAX(id_estudio) FROM estudio))"
    )
    op.execute(
        "SELECT setval('usuario_id_user_seq', (SELECT MAX(id_user) FROM usuario))"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM solicitacoes WHERE fk_id_estudante >= 1")
    op.execute("DELETE FROM contato WHERE fk_id_user >= 1")
    op.execute('DELETE FROM estudante_aula WHERE fk_id_estudante >=1')
    op.execute("DELETE FROM estudante WHERE fk_id_user >= 1")
    
    op.execute("DELETE FROM solicitacoes WHERE fk_id_estudante >= 1")
    
    op.execute("DELETE FROM adm_plus WHERE fk_id_user >= 1")
    op.execute('DELETE FROM aula WHERE fk_id_professor>=1')
    op.execute('DELETE FROM professor WHERE FK_ID_USER >=1')
    op.execute('DELETE FROM ADMINISTRACAO WHERE FK_ID_USER >=1')
    op.execute('DELETE FROM recepcionista WHERE FK_ID_USER >=1')
    # ADICIONE ESTA LINHA PARA LIMPAR OS ENDEREÇOS
    op.execute("DELETE FROM endereco WHERE fk_id_user >= 1")

    # 2. Agora que as dependências foram removidas, delete os usuários.
    op.execute("DELETE FROM usuario WHERE id_user >= 1")

    # 3. Por fim, delete os estúdios.
    op.execute("DELETE FROM estudio WHERE id_estudio >= 1")

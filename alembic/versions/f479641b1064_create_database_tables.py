"""create database tables

Revision ID: f479641b1064
Revises: 
Create Date: 2025-09-29 11:22:04.746000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f479641b1064'
# down_revision: Union[str, Sequence[str], None] = '0c7b19c695bf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    #PARTE DE USUARIOS
    op.create_table(
    'usuario',
        sa.Column('id_user', sa.Integer, primary_key=True, nullable=False, autoincrement=True),
        sa.Column('name_user', sa.String(100), nullable=False),
        sa.Column('nasc_user', sa.Date, nullable=True),
        sa.Column('tipo_doc_user', sa.Enum('cpf', 'cnpj',name='tipo_doc_user_enum'), nullable=False),
        sa.Column('num_doc_user', sa.String(14), nullable=False),
        sa.Column('lv_acesso', sa.Enum('SUPREMO', 'COLABORADOR', 'MIN', 'SENSEI', name='lv_acesso_enum'))
    )
    op.create_table(
        'endereco',
        sa.Column('id_endereco', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False),
        sa.Column('tipo_endereco', sa.Enum('RESIDENCIAL', 'COMERCIAL', name='tipo_endereco_enum'), nullable=False),
        sa.Column('endereco', sa.String(255), nullable=False),
        sa.Column('cep', sa.String(8), nullable=True)
    )
    op.create_table(
        'email',
        sa.Column('id_email', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False),
        sa.Column('tipo_email',sa.Enum('PESSOAL', 'COMERCIAL', name='tipo_email_enum'), nullable=False),
        sa.Column('endereco_email', sa.String(255), nullable=False)
    )
    op.create_table(
        'contato',
        sa.Column('id_contato', sa.Integer,primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False),
        sa.Column('tipo_contato', sa.Enum('RESIDENCIAL', 'COMERCIAL', 'FAMILIAR', name='tipo_contato_enum')),
        sa.Column('numero_contato', sa.String(255), nullable=False)
    )


    #parte de estudante e professores

    op.create_table(
        'estudante',
        sa.Column('id_estudante', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False),
        sa.Column('profissao_user', sa.String(255), nullable= True),
        sa.Column('historico_medico', sa.String(255), nullable=False),
    )
    op.create_table(
        'professor',
        sa.Column('id_professor', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False),
        sa.Column('tipo_especializacao', sa.Enum('cref', 'crefita', name='tipo_especializacao_enum'), nullable=False),
    )
    op.create_table(
        'administracao',
        sa.Column('id_adm', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False)

    )
    op.create_table(
        'recepcionista',
        sa.Column('id_recepcionista', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False)
    )
    #tabela dos registro feitos pelo instrutor/professor sobre um aluno.
    #mongo_arquivo é referente ao ObjectID do aluno, nela terá registrado uma array com mais objectIDs referentes aos seus registros
    op.create_table(
        'registro_do_aluno',
        sa.Column('id_resgitro', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante'), nullable=False),
        sa.Column('fk_id_professor', sa.Integer, sa.ForeignKey('professor.id_professor'), nullable=False),
        sa.Column('mongo_arquivo_id', sa.String(255), nullable=False)
    )
    #tabela de ligação entre estudante e professor
    op.create_table('professor_estudante',
    sa.Column('fk_id_estudante', sa.Integer,sa.ForeignKey('estudante.id_estudante'), nullable=False),               
    sa.Column('fk_id_professor', sa.Integer, sa.ForeignKey('professor.id_professor'), nullable=False)
    )

    #tabeela estudio
    op.create_table(
        'estudio', 
        sa.Column('id_estudio', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('endereco_estudio', sa.String(255),nullable=False, unique=True),
        sa.Column('cep_estudio', sa.String(8), nullable=False),
        sa.Column('mongo_registros_estudio', sa.String(255), nullable=False)

    )

    #tabelas de aula
    op.create_table(
        'aula', 
        sa.Column('id_aula', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('data_aula', sa.DateTime, nullable=False),
        sa.Column('titulo_aula', sa.String(255), nullable=False),
        sa.Column('desc_aula', sa.String(255), nullable=True),
        sa.Column('fk_id_estudio', sa.Integer, sa.ForeignKey('estudio.id_estudio'), nullable=False),
        sa.Column('fk_id_professor', sa.Integer, sa.ForeignKey('professor.id_professor'), nullable=False),
    )
    #tabela de ligação entre aula e o estudante
    op.create_table(
        'estudante_aula',
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante'), nullable=False),
        sa.Column('fk_id_aula', sa.Integer, sa.ForeignKey('aula.id_aula'),nullable=False)

    )

    #tabelas de finaças


def downgrade() -> None:
    """Downgrade schema."""
    # Dropzin nas tabelas em ordem inversa(do filho para o pai)
    
    # Tabelas de Ligação
    op.drop_table('estudante_aula')
    op.drop_table('professor_estudante')
    
    # Tabelas de Entidade de Negócio
    op.drop_table('aula')
    op.drop_table('estudio')
    op.drop_table('registro_do_aluno')
    op.drop_table('administracao')
    op.drop_table('recepcionista')
    op.drop_table('professor')
    op.drop_table('estudante')

    # Tabelas de Contato/Endereço
    op.drop_table('contato')
    op.drop_table('email')
    op.drop_table('endereco')
    
    # Tabela Principal
    op.drop_table('usuario')
    
    # DRop nos tipos de ENUM criados (CRUCIAL no PostgreSQL)
    # MUDANÇA: Adicionado o novo ENUM 'tipo_especializacao_enum'.
    op.execute('DROP TYPE tipo_contato_enum;')
    op.execute('DROP TYPE tipo_email_enum;')
    op.execute('DROP TYPE tipo_endereco_enum;')
    op.execute('DROP TYPE lv_acesso_enum;')
    op.execute('DROP TYPE tipo_doc_user_enum;')
    op.execute('DROP TYPE tipo_especializacao_enum;')


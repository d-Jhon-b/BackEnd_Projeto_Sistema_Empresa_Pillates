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
    #feito
    values_string_function_now:str = "'now()'"
    value_cascade_constraint_drop:str = 'CASCADE'
    value_set_null:str ='SET NULL'
    
    op.create_table(
    'usuario',
        sa.Column('id_user', sa.Integer, primary_key=True, nullable=False, autoincrement=True),
        sa.Column('name_user', sa.String(100), nullable=False),
        sa.Column('foto_user', sa.String(255), nullable=True, default='fotoUser.png'),
        sa.Column('nasc_user', sa.Date, nullable=True),
        sa.Column('tipo_doc_user', sa.Enum('cpf', 'cnpj',name='tipo_doc_user_enum'), nullable=False),
        sa.Column('num_doc_user', sa.String(14), nullable=False),
        sa.Column('lv_acesso', sa.Enum('supremo', 'colaborador', 'instrutor','aluno',  name='lv_acesso_enum'),nullable=False),
        
        #aplicaçõe de conta:
        sa.Column('tipo_email',sa.Enum('pessoal', 'comercial', name='tipo_email_enum'), nullable=False),
        sa.Column('email_user', sa.String(255), nullable=False),
        sa.Column('senha_user', sa.String(255), nullable= False),
            
        #Criar uma contraint para tornar o documento de um usuario unico em todo o sistema
        sa.UniqueConstraint('email_user', name='uq_usuario_email_user'),
        sa.UniqueConstraint('num_doc_user', name='uq_usuario_num_doc')
    )
    #feito
    op.create_table(
        'endereco',
        sa.Column('id_endereco', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False),
        sa.Column('tipo_endereco', sa.Enum('residencial', 'comercial', name='tipo_endereco_enum'), nullable=False),
        sa.Column('endereco', sa.String(255), nullable=False),
        sa.Column('cep', sa.String(8), nullable=True)
    )
    # op.create_table(
    #     'email',
    #     sa.Column('id_email', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
    #     sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=False),
    #     sa.Column('tipo_email',sa.Enum('PESSOAL', 'COMERCIAL', name='tipo_email_enum'), nullable=False),
    #     sa.Column('endereco_email', sa.String(255), nullable=False),
    #     sa.UniqueConstraint('fk_id_user','endereco_email', name='uq_email_user_email')
    # )
    #feito
    op.create_table(
        'contato',
        sa.Column('id_contato', sa.Integer,primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False),
        sa.Column('tipo_contato', sa.Enum('residencial', 'comercial', 'familiar', name='tipo_contato_enum'), nullable=False),
        sa.Column('numero_contato', sa.String(255), nullable=False)
    )


    #parte de estudante e professores
    #feito schema src.model.userMOdel.typeUser.aluno.py
    op.create_table(
        'estudante',
        sa.Column('id_estudante', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False),
        sa.Column('profissao_user', sa.String(255), nullable= True),
        sa.Column('historico_medico', sa.String(255), nullable=False),
    )
    #feito src.model.userModel.typeUser.instrutor.py
    op.create_table(
        'professor',
        sa.Column('id_professor', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False),
        sa.Column('tipo_especializacao', sa.Enum('cref', 'crefita', name='tipo_especializacao_enum'), nullable=False),
        sa.Column('numero_de_registro', sa.String(50), nullable=False),
        sa.Column('formacao', sa.String(255), nullable=True),  
        sa.Column('data_contratacao', sa.Date, nullable=False)
    )
    #feito
    op.create_table(
        'administracao',
        sa.Column('id_adm', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False)

    )
    #feito
    op.create_table(
        'recepcionista',
        sa.Column('id_recepcionista', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False)
    )
    """
    Tabela adicional solicitada pela cliente, para maior conforto da situação atual
    """
    #não aplicado
    op.create_table(
        'adm_plus',
        sa.Column('id_adm_plus', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user', ondelete=value_cascade_constraint_drop), nullable=False)

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
    #feito
    op.create_table(
        'estudio', 
        sa.Column('id_estudio', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('endereco_estudio', sa.String(255),nullable=False, unique=True),
        sa.Column('cep_estudio', sa.String(8), nullable=False),
        sa.Column('mongo_registros_estudio', sa.String(255), nullable=False)
    )

    #tabelas de aula
    #feito
    op.create_table(
        'aula', 
        sa.Column('id_aula', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('data_aula', sa.DateTime, nullable=False),
        sa.Column('titulo_aula', sa.String(255), nullable=False),
        sa.Column('desc_aula', sa.String(255), nullable=True),
        sa.Column('fk_id_estudio', sa.Integer, sa.ForeignKey('estudio.id_estudio'), nullable=False),
        sa.Column('fk_id_professor', sa.Integer, sa.ForeignKey('professor.id_professor'), nullable=False),
        sa.Column('fk_id_professor_substituto', sa.Integer, sa.ForeignKey('professor.id_professor'), nullable=True),
        
        sa.CheckConstraint('fk_id_professor != fk_id_professor_substituto', name='chk_titular_substituto_diferentes')
    )

    #tabela de ligação entre aula e o estudante
    #feito
    op.create_table(
        'estudante_aula',
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante'), nullable=False, primary_key=True),
        sa.Column('fk_id_aula', sa.Integer, sa.ForeignKey('aula.id_aula'),nullable=False, primary_key=True),
        sa.Column('tipo_de_aula', sa.Enum('normal', 'experimental', 'reposicao',name="enum_tipo_de_aula"), nullable=False)

    )

    #tabelas de planos
    #feito
    op.create_table(
        'planos',
        sa.Column('id_plano', sa.Integer ,primary_key=True, autoincrement=True, nullable=False),
        sa.Column('tipo_plano', sa.Enum('mensal', 'trimestral', 'semestral','anual', name='enum_tipo_plano'), nullable=False),
        sa.Column('modalidade_plano', sa.Enum('1x_semana', '2x_semana', '3x_semana', name= 'enum_modalidade_plano'), nullable=False),
        
        sa.Column('descricao_plano', sa.String(255), nullable=True),
        sa.Column('valor_plano', sa.Numeric(precision=10, scale=2)),
        sa.CheckConstraint('valor_plano <= 999.99', name='chk_valor_plano_max'),


        sa.Column('qtde_aulas_totais', sa.Integer, nullable=False),
        
        # Aplicação da restrição de valor máximo para qtde_aulas_totaia
        sa.CheckConstraint('qtde_aulas_totais <= 1000', name='chk_aulas_totais_max')

    )

    op.create_table(
        'planos_personalizados',
        sa.Column('id_plano_personalizado', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('nome_plano', sa.String(255), nullable=False),
        sa.Column('tipo_plano_livre', sa.String(100), nullable=False), # String livre
        sa.Column('modalidade_plano_livre', sa.String(100), nullable=False), # String livre
        
        sa.Column('descricao_plano', sa.String(255), nullable=True),
        sa.Column('valor_plano', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('qtde_aulas_totais', sa.Integer, nullable=False),
        sa.Column('is_temporario', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('data_criacao', sa.DateTime, nullable=False, server_default=sa.text(values_string_function_now)),
        sa.Column('data_validade', sa.DateTime, nullable=True),
        
        # Mantendo as constraints de CHECK para valor e quantidade, mas com nome diferente
        sa.CheckConstraint('valor_plano <= 999.99', name='chk_valor_plano_personalizado_max'),
        sa.CheckConstraint('qtde_aulas_totais <= 1000', name='chk_aulas_totais_personalizado_max')
    )

    #tabela de adesao de plano
    #não aplicado
    op.create_table(
        'adesao_plano',
        sa.Column('id_adesao_plano', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante', ondelete=value_set_null), nullable=True),
        sa.Column('fk_id_plano', sa.Integer, sa.ForeignKey('planos.id_plano', ondelete=value_set_null), nullable=True),
        sa.Column('fk_id_plano_personalizado', sa.Integer, sa.ForeignKey('planos_personalizados.id_plano_personalizado', ondelete=value_set_null), nullable=True),
        sa.Column('data_adesao', sa.DateTime, nullable=False, server_default=sa.text(values_string_function_now)),
        sa.Column('data_validade', sa.DateTime, nullable=False)
    )

    #tabela de contrato
    #não aplicado
    op.create_table(
        'contrato',
        sa.Column('id_contrato', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante', ondelete=value_cascade_constraint_drop), nullable=True),
        sa.Column('fk_id_plano', sa.Integer, sa.ForeignKey('planos.id_plano', ondelete=value_cascade_constraint_drop), nullable=True),
        sa.Column('fk_id_adesao_plano', sa.Integer, sa.ForeignKey('adesao_plano.id_adesao_plano', ondelete=value_cascade_constraint_drop), nullable=True),
        sa.Column(
            'fk_id_plano_personalizado', 
            sa.Integer, 
            sa.ForeignKey('planos_personalizados.id_plano_personalizado', ondelete=value_cascade_constraint_drop), 
            nullable=True
        ),
        sa.Column('valor_final', sa.Numeric(precision=10, scale=2), nullable=False), 
        sa.Column('data_inicio', sa.DateTime, nullable=False),
        sa.Column('data_termino', sa.DateTime, nullable=False),
        sa.Column('aulas_restantes', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('status_contrato', sa.Enum('ativo', 'suspenso', 'cancelado', 'expirado', name='enum_status_contrato'), nullable=False),
        sa.CheckConstraint('fk_id_plano IS NULL OR fk_id_plano_personalizado IS NULL', name='chk_one_plan_fk_active')
    )
    #não aplicado
    op.create_table(
        'venda_extra',
        sa.Column('id_venda_extra',sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante', ondelete=value_cascade_constraint_drop), nullable=True),
        sa.Column('descricao', sa.String(255), nullable=True),
        sa.Column('valor_venda_extra', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('data_venda', sa.DateTime, nullable=False),
    )
    #não aplicado
    op.create_table(
        'pagamento',
        sa.Column('id_pagamento', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('fk_id_contrato', sa.Integer, sa.ForeignKey('contrato.id_contrato', ondelete=value_cascade_constraint_drop), nullable=True),
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante', ondelete=value_cascade_constraint_drop), nullable=False),
        sa.Column('fk_id_venda_extra', sa.Integer, sa.ForeignKey('venda_extra.id_venda_extra'), nullable=True),
        sa.Column('valor_pagamento',sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('data_pagamento', sa.DateTime, nullable=True),
        sa.Column('data_vencimento', sa.DateTime, nullable=False),
        sa.Column('metodo_pagamento', sa.Enum('cartao', 'pix', 'dinheiro', name='enum_metodo_pagamento'), nullable=True),
        sa.Column('status_pagamento', sa.Enum('pago', 'pendente', 'atrasado', name='enum_status_pagamento'), nullable=False),
        sa.Column('descricao_pagamento', sa.String(255), nullable=False),

        sa.CheckConstraint(
            '(fk_id_contrato IS NOT NULL AND fk_id_venda_extra IS NULL) OR '
            '(fk_id_contrato IS NULL AND fk_id_venda_extra IS NOT NULL)',
            name='chk_one_payment_source'
        )
    )
    #não aplicado
    op.create_table(
        'solicitacoes',
        sa.Column('id_solicitacao', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        # sa.Column('fk_id_user', sa.Integer, sa.ForeignKey('usuario.id_user'), nullable=True),
        sa.Column('fk_id_estudante', sa.Integer, sa.ForeignKey('estudante.id_estudante'), nullable=False),        
        
        sa.Column('fk_id_estudio', sa.Integer, sa.ForeignKey('estudio.id_estudio'), nullable=False),
        sa.Column('tipo_de_solicitacao', sa.Enum('aula', 'plano','pagamento','outros', name='enum_solicitacao'), nullable=False),
        sa.Column('menssagem', sa.Text, nullable=True),
        # sa.Column('status_solicitacao', sa.Enum('atendida', 'recusada', 'em espera', name='enum_status_solicitacao'), nullable=False, default="em espera"),
        sa.Column('status_solicitacao', sa.Enum('atendida', 'recusada', 'em espera', name='enum_status_solicitacao'), nullable=False, server_default=sa.text("'em espera'")),
        sa.Column('data_criacao', sa.DateTime, nullable=False, server_default=sa.text(values_string_function_now)),
        sa.Column('data_resposta', sa.DateTime, nullable=True),
        sa.Column('acao_solicitacao_aula', sa.Enum('AGENDAMENTO', 'REAGENDAMENTO', 'CANCELAMENTO', name='enum_acao_solicitacao_aula'), nullable=True),
        sa.Column('acao_solicitacao_plano', sa.Enum(
            'MUDANCA_PLANO', 
            'CANCELAMENTO_PLANO', 
            'RENOVACAO_PLANO', 
            name='enum_acao_solicitacao_plano'
        ), nullable=True), 
        sa.Column(
            'fk_id_aula_referencia', 
            sa.Integer, 
            sa.ForeignKey('aula.id_aula'), 
            nullable=True, 
            comment="ID da aula que está sendo referenciada (para reagendamento/cancelamento)"
        ),
        sa.Column('data_sugerida', sa.DateTime, nullable=True),
        
        sa.Column(
            'fk_id_novo_plano', 
            sa.Integer, 
            sa.ForeignKey('planos.id_plano'), 
            nullable=True
        ),
        sa.Column(
            'fk_id_novo_plano_personalizado', 
            sa.Integer, 
            sa.ForeignKey('planos_personalizados.id_plano_personalizado'), 
            nullable=True
        ),
        sa.CheckConstraint(
            '(fk_id_novo_plano IS NULL) OR (fk_id_novo_plano_personalizado IS NULL)', 
            name='chk_one_new_plan_fk_active'
        ),

    
    )   


def downgrade() -> None:
    """Downgrade schema."""
    

    # Dropando as contraints antes de dropar as tab elas ligadas a User:
    # Pagamento depende de Contrato, Venda_Extra e Estudante
    op.drop_table('pagamento')
    
    # Venda_Extra depende de Estudante
    op.drop_table('venda_extra')
    
    # Contrato depende de Estudante e Planos
    op.drop_constraint('chk_one_plan_fk_active', 'contrato', type_='check')

    op.drop_table('contrato')
    # Adesao_Plano depende de Usuario
    op.drop_table('adesao_plano')
    
    
    # 2. DROP DAS TABELAS DE LIGAÇÃO
    
    # Estudante_Aula depende de Estudante e Aula
    op.drop_table('estudante_aula')
    
    # Professor_Estudante depende de Professor e Estudante
    op.drop_table('professor_estudante')
    
    # Registro_do_Aluno depende de Estudante e Professor
    op.drop_table('registro_do_aluno')
    
    # 3. DROP DAS TABELAS DE ENTIDADE DE NEGÓCIO
    # Remover constraint de check da tabela 'aula'
    op.drop_constraint('chk_titular_substituto_diferentes', 'aula', type_='check')
    
    op.drop_constraint('chk_one_new_plan_fk_active', 'solicitacoes',type_='check')
    # Aula depende de Estudio e Professor
    op.drop_table('solicitacoes')
    op.drop_table('aula')
    op.drop_table('estudio')

    op.drop_constraint('chk_valor_plano_max', 'planos', type_='check')
    op.drop_constraint('chk_aulas_totais_max', 'planos', type_='check')
    op.drop_table('planos')
    
    op.drop_constraint('chk_valor_plano_personalizado_max', 'planos_personalizados', type_='check')
    op.drop_constraint('chk_aulas_totais_personalizado_max', 'planos_personalizados', type_='check')
    op.drop_table('planos_personalizados')

    # 4. DROP DAS TABELAS DE PAPÉIS (DEPENDEM DE USUARIO)
    
    op.drop_table('adm_plus')
    op.drop_table('administracao')
    op.drop_table('recepcionista')
    op.drop_table('professor')
    op.drop_table('estudante')

    # 5. DROP DAS CONSTRAINTS ÚNICAS (SEPARADAMENTE)
    
    # Constraint na tabela 'usuario'
    op.drop_constraint('uq_usuario_email_user', 'usuario', type_='unique')
    op.drop_constraint('uq_usuario_num_doc', 'usuario', type_='unique')
    # Constraint na tabela 'email'
    # op.drop_constraint('uq_email_user_email', 'email', type_='unique') 

    # 6. DROP DAS TABELAS DE DETALHES DO USUÁRIO
    
    # Dependem de Usuario
    op.drop_table('contato')
    # op.drop_table('email')
    op.drop_table('endereco')
    
    # 7. DROP DA TABELA PRINCIPAL
    
    op.drop_table('usuario')
    
    # 8. DROP DOS TIPOS ENUM (CRUCIAL NO POSTGRESQL)

    op.execute('DROP TYPE enum_tipo_de_aula;')
    op.execute('DROP TYPE enum_solicitacao;')
    op.execute('DROP TYPE enum_status_solicitacao;')
    op.execute('DROP TYPE enum_status_pagamento;')

    op.execute('DROP TYPE enum_metodo_pagamento;')
    op.execute('DROP TYPE enum_status_contrato;')
    # op.execute('DROP TYPE enum_num_aulas_semana;')
    op.execute('drop type enum_modalidade_plano;')
    op.execute('DROP TYPE enum_tipo_plano;')
    op.execute('DROP TYPE tipo_especializacao_enum;')
    op.execute('DROP TYPE tipo_contato_enum;')
    op.execute('DROP TYPE tipo_email_enum;')
    op.execute('DROP TYPE tipo_endereco_enum;')
    op.execute('DROP TYPE lv_acesso_enum;')
    op.execute('DROP TYPE tipo_doc_user_enum;')
    op.execute('DROP TYPE enum_acao_solicitacao_plano;') 
    op.execute('DROP TYPE enum_acao_solicitacao_aula;')
    
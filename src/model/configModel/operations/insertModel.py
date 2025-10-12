from typing import Dict, Any
import psycopg2 
import logging

from src.model.configModel.userSettings.valuesUser import NivelAcessoEnum 
# from src.dat.database.connPostGre import PostGreModel # Sua importação de conexão
from src.database.connPostGre import PostGreModel


# Configuração básica de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class InserValues:
    """
    Classe responsável por executar os comandos INSERT no banco de dados.
    """
    #Mapeamento dos niveis de acesso
    TABELAS_SUBTIPO = {
        NivelAcessoEnum.ALUNO.value: 'estudante',
        NivelAcessoEnum.INSTRUTOR.value: 'professor',
        NivelAcessoEnum.COLABORADOR.value: 'administracao', 
        NivelAcessoEnum.SUPREMO.value: 'administracao',
    }

    #tipoUser e usa a NivelAcessoEnum.
    def __init__(self, tipoUser: str):
        self.tipoUser = tipoUser.lower()
        self.pode_inserir = False
        self.conn = None

        # Validação de Permissões (APENAS supremo e colaborador podem inserir)
        if self.tipoUser in [NivelAcessoEnum.SUPREMO.value, NivelAcessoEnum.COLABORADOR.value]:
            logging.info(f'Permissão de alteração concedida para: {self.tipoUser}')
            
            # Inicialização da conexão
            self.postGre = PostGreModel()
            self.conn = self.postGre.connect_db()

            if self.conn is not None:
                self.pode_inserir = True
            else:
                logging.error("Falha na conexão com o banco de dados. Inserções desativadas.")
        else:
            logging.warning(f'Permissão negada. Usuário "{self.tipoUser}" não pode inserir novos usuários.')


    def inserirNovoUsuario(self, data: Dict[str, Any]):
        
        if not self.pode_inserir or self.conn is None:
            return {'status': 'error', 'message': 'Operação não autorizada ou conexão indisponível.'}

        cursor = None
        try:
            cursor = self.conn.cursor()
            
            # INSERT TABELA 'usuario'
            comand_usuario = """
            INSERT INTO usuario (
                name_user, foto_user, nasc_user, tipo_doc_user, 
                num_doc_user, lv_acesso, tipo_email, email_user, senha_user
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_user;
            """
            
            values_usuario = (
                data['name_user'],
                data['foto_user'],
                data['nasc_user'], 
                data['tipo_doc_user'],
                data['num_doc_user'],
                data['lv_acesso'], 
                data['tipo_email'],
                data['email_user'],
                data['senha_user'] 
            )

            cursor.execute(comand_usuario, values_usuario)
            id_user_fk = cursor.fetchone()[0]
            
            logging.info(f"Usuário base inserido. id_user: {id_user_fk}")

            
            # INSERT TABELA DE TIPO DE USUÁRIO
            
            nivel_acesso = data['lv_acesso']
            tabela_subtipo = self.TABELAS_SUBTIPO.get(nivel_acesso)
            
            if tabela_subtipo:
                
                comand_subtipo = f"INSERT INTO {tabela_subtipo} (fk_id_user) VALUES (%s)"
                values_subtipo = (id_user_fk,)
                
                # Lógica para tabelas com campos extras dependendo no nivel de acesso atribuido:(Estudante e Professor)
                if nivel_acesso == NivelAcessoEnum.ALUNO.value:
                    comand_subtipo = f"""
                    INSERT INTO estudante (fk_id_user, profissao_user, historico_medico) 
                    VALUES (%s, %s, %s)
                    """
                    values_subtipo = (
                        id_user_fk,
                        data.get('profissao_user'),
                        data.get('historico_medico')
                    )
                elif nivel_acesso == NivelAcessoEnum.INSTRUTOR.value:
                    comand_subtipo = f"""
                    INSERT INTO professor (fk_id_user, tipo_especializacao) 
                    VALUES (%s, %s)
                    """
                    values_subtipo = (
                        id_user_fk,
                        data.get('tipo_especializacao')
                    )

                cursor.execute(comand_subtipo, values_subtipo)
                logging.info(f"Inserido na tabela de subtipo: {tabela_subtipo}")


            # insert TABELA 'contato'
            contatos_data = data.get('contatos', [])
            if contatos_data:
                comand_contato = """
                INSERT INTO contato (fk_id_user, tipo_contato, numero_contato) 
                VALUES (%s, %s, %s)
                """
                contatos_a_inserir = [
                    (id_user_fk, c['tipo_contato'], c['numero_contato'])
                    for c in contatos_data
                ]
                cursor.executemany(comand_contato, contatos_a_inserir)
                logging.info(f"Inseridos {len(contatos_a_inserir)} contatos.")

            
            # INSERT TABELA 'endereco'
            enderecos_data = data.get('enderecos', [])
            if enderecos_data:
                comand_endereco = """
                INSERT INTO endereco (fk_id_user, tipo_endereco, endereco, cep) 
                VALUES (%s, %s, %s, %s)
                """
                enderecos_a_inserir = [
                    (id_user_fk, e['tipo_endereco'], e['endereco'], e['cep'])
                    for e in enderecos_data
                ]
                cursor.executemany(comand_endereco, enderecos_a_inserir)
                logging.info(f"Inseridos {len(enderecos_a_inserir)} endereços.")

            self.conn.commit()
            return {'status': 'success', 'message': f'Usuário e dados relacionados inseridos com sucesso! ID: {id_user_fk}'}

        except psycopg2.Error as db_error:
            if self.conn:
                self.conn.rollback() 
            logging.error(f"ERRO DE BANCO DE DADOS: {db_error}")
            return {'status': 'error', 'message': f'Erro ao inserir no banco: {db_error.pgerror}'}
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logging.error(f"ERRO INESPERADO: {e}")
            return {'status': 'error', 'message': f'Erro inesperado: {e}'}
            
        finally:
            if cursor:
                cursor.close()



# from src.model.configModel.userSettings.valuesUser import TipoContatoEnum, TipoDocumentoEnum, TipoEmailEnum, TipoEnderecoEnum

# senha_com_hash_teste = "$2b$12$4Lp5p.G4vG4Q8l.pE5Y5o.iK7c.jE7/h4W4Q6.yY7/h4W4Q6.yY7/h4W4Q6.yY"
# from datetime import date
# data_aluno = {
#     # Campos base da tabela 'usuario'
#     'name_user': 'Maria Teste Aluna',
#     'foto_user': None,
#     'nasc_user': date(1995, 5, 10),
#     'tipo_doc_user': TipoDocumentoEnum.CPF.value,
#     'num_doc_user': '98005432109',
#     'lv_acesso': NivelAcessoEnum.ALUNO.value, # CRÍTICO: Define a tabela de subtipo
#     'tipo_email': TipoEmailEnum.PESSOAL.value,
#     'email_user': 'maria.aluna@teste.com',
#     'senha_user': senha_com_hash_teste,
    
#     # Campos específicos do ALUNO (subtipo 'estudante')
#     'profissao_user': 'Estudante',
#     'historico_medico': 'Nenhuma condição pré-existente.',
    
#     # Relacionamento 1:N
#     'contatos': [
#         {'tipo_contato': TipoContatoEnum.RESIDENCIAL.value, 'numero_contato': '11999998888'},
#     ],
#     'enderecos': [
#         {'tipo_endereco': TipoEnderecoEnum.RESIDENCIAL.value, 'endereco': 'Rua dos testes, 123', 'cep': '01000000'}
#     ]
# }
# inserINstance = InserValues('colaborador')
# insertTest = inserINstance.inserirNovoUsuario(data_aluno)
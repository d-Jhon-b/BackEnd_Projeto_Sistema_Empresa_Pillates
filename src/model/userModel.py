from src.model.userModel.userConfig import Usuario
from src.model.userModel.valuesUser.enderecoUser import Endereco
from src.model.userModel.valuesUser.contatoUser import Contato

from src.database.connPostGreNeon import CreateSessionPostGre

from src.model.userModel.validations.validarEmail import ValidarEmail
from src.model.userModel.validations.ValidarSenha import ValidarSenha
# from src.model.UserModel.operations.insertTypeUser import InsertTypeUser
from src.model.userModel.typeUser.aluno import Estudante
from src.model.userModel.typeUser.colaborador import Administracao, Recepcionista
from src.model.userModel.typeUser.Instrutor import Professor
from src.model.estudioModel.estudioConfig import Estudio

from src.model.utils.fk_id_user import AnexarFkUser
from src.model.utils.HashPassword import HashPassword

from datetime import date
from typing import Dict, Union, Optional
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

# import logging

class UserModel():
    def __init__(self,tipoUser:str):

        self.tipoUser = tipoUser
        self.permissoes = ['supremo', 'colaborador']
        self.createSession = None
        self.session = None
        self.stmt = None
    
    def create_new_user(self, user_data:dict, endereco_data:dict=None, contato_data:dict =None, extra_data:dict=None):
        try:
            self.createSession = CreateSessionPostGre()
            self.session = self.createSession.get_session()

            if self.tipoUser not in self.permissoes:
                print(f'Você não tem permissão de criar um novo usuario')
                return None
            # if not ValidarEmail.validar_email(self.session, user_data['email_user']):
            #     return None


            if ValidarEmail.validar_email(self.session, user_data['email_user']):
                print(f'fasfasfaandaskodnasdkansdkoasndkasndkoad\n\n\n/n')
                return None
            
            
            # if not self.session:
            #     print(f'erro ao obter sessão')
            #     return None
            

            #tratamento da senha para hash- bcript
            self.password_user = user_data.get('senha_user')
            if not self.password_user:
                return {'status': 'error', 'message': 'Campo de senha Obrigatorio FDP'}
            self.password_user_hash = HashPassword.hash_password(self.password_user)
            user_data['senha_user'] = self.password_user_hash.decode('utf-8')

            self.new_user = Usuario(**user_data)
            self.session.add(self.new_user)
            self.session.flush()
            self.fk_id_user = self.new_user.id_user


            #verifica o endereço e contato e insere
            if endereco_data:
                self.endereco = Endereco(**AnexarFkUser.anexar_fk_user(endereco_data, self.fk_id_user))
                self.session.add(self.endereco)

            if contato_data:
                self.contato = Contato(**AnexarFkUser.anexar_fk_user(contato_data, self.fk_id_user))
                self.session.add(self.contato)


            self.lv_acesso = user_data.get('lv_acesso')

            if self.lv_acesso == 'aluno' and extra_data:
                self.estudante = Estudante(fk_id_user =self.fk_id_user, **extra_data)
                self.session.add(self.estudante)

            if self.lv_acesso == 'colaborador':
                self.adm = Administracao(fk_id_user=self.fk_id_user)
                self.session.add(self.adm)
                if extra_data and extra_data.get('tipo') == 'recepcionista':
                    self.recep = Recepcionista(fk_id_user = self.fk_id_user)
                    self.session.add(self.recep)


            self.session.commit()
            print(f'usuarios inserido com sucesso')
            # create_type_user = InsertTypeUser.insertTypeUser()
            
            return self.new_user
        except SQLAlchemyError as AlchemyError:
            self.session.rollback()
            print(f'Erro ao inserir dados no banco:\n{AlchemyError}')
            return None
        
        except Exception as err:
            print(f'Erro ao processar a inserção no banco')
            return None
        finally:
            self.session.close()
        
    # def login_user(self, email, password):
    def login_user(self, user_data:dict):
        try:
            self.createSession = CreateSessionPostGre()
            self.session = self.createSession.get_session()

            self.email_user = user_data.get('email_user')
            if not ValidarEmail.validar_email(self.session, self.email_user):
                return None
            
            self.password_user = user_data.get('senha_user')
            self.byte_password_user = self.password_user.encode('utf-8')
            self.storege_password = ValidarSenha.validar_senha(self.session, self.email_user)
            self.senha_valida = bcrypt.checkpw(self.byte_password_user, self.storege_password.encode('utf-8'))
            
            if self.senha_valida:
                self.stmt = select(Usuario).where(Usuario.email_user == self.email_user)
                self.user = self.session.execute(self.stmt).scalar_one_or_none()
                print(self.user)
                return self.user
            else:
                print('Erro ao fazer login\n\nSenha Incorreta')
                return None
            

        except SQLAlchemyError as AlchemyError:
            self.session.rollback()
            print(f'Erro ao fazer login:\n{AlchemyError}')
            return None
        
        except Exception as err:
            print(f'Erro ao processar Login')
            return None
        finally:
            self.session.close()

    def select_user_id(self, user_id):
        try:
            self.createSession =CreateSessionPostGre()
            self.session = self.createSession
            self.stmt = select(Usuario).jo


        except SQLAlchemyError as AlvchemyErrors:
            print(f'Erro ao relizar seleção: {AlvchemyErrors}')
            return None
        except Exception as err:
            print(f'Erro ao realiza seleção {err}')
            return None
        finally:
            print(f'Fechando sessão....')
            self.session.close()
        
    def select_all_users():
        pass

# from datetime import date

# user_data = {
#     "name_user": "Jhon da Silva",
#     "foto_user": None,
#     "nasc_user": date(1990, 5, 17),
#     "tipo_doc_user": "cpf",
#     "num_doc_user": "48675969877",
#     "lv_acesso": "colaborador",
#     "tipo_email": "pessoal",
#     "email_user": "tiocatador@gmail.com",
#     "senha_user": "962266514",
#     "estudio_aplicado": "itaquera",
#     "fk_id_estudio":1
# }

# endereco_data = {
#     "tipo_endereco": "residencial",
#     "endereco": "Rua Exemplo, 123",
#     "cep": "12345678"
# }

# contato_data = {
#     "tipo_contato": "residencial",
#     "numero_contato": "11999999999"
# }

# extra_data = {
#     "profissao_user": "Estudante",
#     "historico_medico": "Nenhum"
# }
# user_model = UserModel('supremo')
# user_model.create_new_user(user_data, endereco_data, contato_data, extra_data)

# data = {
#     "email_user": "tiocatador@gmail.com",
#     "senha_user":"962266514" 
# }
# user_model = UserModel('aluno')
# user_model.create_new_user(user_data, endereco_data, contato_data, extra_data)
# print(user_model.login_user(data))
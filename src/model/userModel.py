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
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

# import logging

class UserModel():
    def __init__(self, db_session:Session):
        self.session = db_session
    
    def create_new_user(self, user_data:dict, endereco_data:dict=None, contato_data:dict =None, extra_data:dict=None):
        try:
            # if not ValidarEmail.validar_email(self.session, user_data['email_user']):
            #     return None
            if ValidarEmail.validar_email(self.session, user_data['email_user']):
                print(f'Email já cadastrado\n\n\n/n')
                return None
            
            self.password_user = user_data.get('senha_user')
            if not self.password_user:
                return {'status': 'error', 'message': 'Campo de senha Obrigatorio'}
            self.password_user_hash = HashPassword.hash_password(self.password_user)
            user_data['senha_user'] = self.password_user_hash.decode('utf-8')
            # print(f'AQUI:\n\n\n\n\n\n{user_data['senha_user']}\n\n\n\n')

            self.new_user = Usuario(**user_data)
            self.session.add(self.new_user)
            self.session.flush()
            self.fk_id_user = self.new_user.id_user

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

            elif self.lv_acesso == 'colaborador':
                self.is_recepcionista = extra_data.get('is_recepcionista', True)

                if self.is_recepcionista:
                    self.session.add(Recepcionista(fk_id_user=self.fk_id_user))
                else:
                    self.adm = Administracao(fk_id_user=self.fk_id_user)
                    self.session.add(self.adm)
                

            elif self.lv_acesso == 'instrutor' and extra_data:
                instrutor = Professor(fk_id_user=self.fk_id_user, **extra_data)
                self.session.add(instrutor)

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

        
    def login_user(self, user_data:dict)->Usuario|None:
        try:
            self.email_user = user_data.get('email_user')
            self.password_user = user_data.get('senha_user')

            if not ValidarEmail.validar_email(self.session, self.email_user):
                return None
            self.storege_password = ValidarSenha.validar_senha(self.session, self.email_user)
            if not self.storege_password:
                return None
            is_valid = bcrypt.checkpw(
                self.password_user.encode('utf-8'), 
                self.storege_password.encode('utf-8')
            )

            if is_valid:
                stmt = select(Usuario).where(Usuario.email_user == self.email_user)
                user = self.session.execute(stmt).scalar_one_or_none()
                return user
            else:
                return None
            

        except SQLAlchemyError as AlchemyError:
            self.session.rollback()
            print(f'Erro ao fazer login:\n{AlchemyError}')
            return None
        
        except Exception as err:
            print(f'Erro ao processar Login {err}')
            return None

    def select_user_id(self, user_id)-> Usuario | None:
        try:
            stmt = (
                select(Usuario)
                .where(Usuario.id_user == user_id)
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.estudante),
                    joinedload(Usuario.professor),    
                    joinedload(Usuario.administracao), 
                    joinedload(Usuario.recepcionista)
                )
            )
            user = self.session.execute(stmt).unique().scalar_one_or_none()
            return user
        except Exception as e:
            print(f'Erro ao realizar seleção por ID: {e}')
            return None
        
    def select_all_users(self, studio_id: int | None = None)->list[Usuario]:
        try:
            stmt = (
                select(Usuario)
                .order_by(Usuario.lv_acesso)
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.estudante),
                    joinedload(Usuario.professor),
                    joinedload(Usuario.administracao),
                    joinedload(Usuario.recepcionista)
                )
            )            
            if studio_id is not None:
                stmt = stmt.where(Usuario.fk_id_estudio == studio_id)
            users = self.session.execute(stmt).scalars().unique().all()
            return users
        except Exception as e:
            print(f'Erro ao selecionar todos os usuários: {e}')
            return []
        
    def delete_user_by_id(self, user_id:int)->Optional[bool]:
        if user_id is None:
            print(f'Usuario não definido para a exclusão')
            return False
        try:
            self.stmt = delete(Usuario).where(Usuario.id_user ==user_id)
            self.res_delete = self.session.execute(self.stmt)
            if self.res_delete.rowcount > 0:
                self.session.commit()
                print(f'Sucesso ao excluir o usuario de ID: {user_id}')
                return True
            else:
                return False
        except SQLAlchemyError as err:
            self.session.rollback()
            print(f'{err}')
            return False
        except Exception as err:
            self.session.rollback()
            print(f'{err}')
            return False


    def select_user_by_email(self, email: str) -> Usuario | None:
            """
            Busca um usuário completo pelo e-mail.
            (Mais eficiente que o ValidarSenha, pois já traz o usuário todo).
            """
            try:
                stmt = select(Usuario).where(Usuario.email_user == email)
                user = self.session.execute(stmt).scalar_one_or_none()
                return user
            except Exception as e:
                print(f'Erro ao selecionar usuário por e-mail: {e}')
                self.session.rollback()
                return None

    def update_user_password(self, user_id: int, hashed_password_str: str) -> bool:
        """
        Atualiza a senha do usuário no banco.
        Espera receber a senha já como string (hash decodificado).
        """
        try:
            user = self.session.query(Usuario).filter(Usuario.id_user == user_id).first()
            
            if not user:
                print(f"Usuário {user_id} não encontrado para atualizar senha.")
                return False
                
            user.senha_user = hashed_password_str
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f'Erro ao atualizar senha do usuário {user_id}: {e}')
            return False


# session_create = CreateSessionPostGre()
# db_session = session_create.get_session()

# try:
#     aluno_test = UserModel(db_session=db_session)
#     aluno_select_all = aluno_test.select_all_users(studio_id=1)
#     for a in aluno_select_all:
#         print(a) 
#     # aluno_select_one = aluno_test.select_user_id(user_id=1)
#     # print(aluno_select_one)

# except Exception as err:
#     print(f"\nErro fatal ao iniciar a sessão ou rodar testes: {err}")
# finally:
#     db_session.close()
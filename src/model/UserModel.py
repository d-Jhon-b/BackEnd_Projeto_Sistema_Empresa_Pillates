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
import traceback
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
            try:
                stmt = select(Usuario).where(Usuario.email_user == email)
                user = self.session.execute(stmt).unique().scalar_one_or_none()
                return user
            except Exception as e:
                print(f'Erro ao selecionar usuário por e-mail: {e}')
                self.session.rollback()
                return None




    def update_user_password(self, user_id: int, hashed_password_str: str) -> bool:
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
        
    def update_user_data(
        self, 
        user_id: int, 
        user_data_to_update: dict, 
        endereco_data_to_update: Optional[list] = None, 
        contato_data_to_update: Optional[list] = None, 
        extra_data_to_update: Optional[dict] = None 
    ) -> Optional[Usuario]:
        try:
            existing_user = self.session.execute(
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
            ).unique().scalar_one_or_none()
            
            if not existing_user: return None

            if user_data_to_update:
                if 'senha_user' in user_data_to_update:
                    password_user = user_data_to_update.pop('senha_user')
                    hashed_password = HashPassword.hash_password(password_user)
                    existing_user.senha_user = hashed_password.decode('utf-8')
                for chave, valor in user_data_to_update.items():
                    setattr(existing_user, chave, valor) 
            

            def handle_one_to_many_update(
                existing_children, 
                incoming_data_list, 
                ChildORM, 
                id_field, 
                fk_field
            ):
                """Gerencia a lógica de UPDATE/INSERT/DELETE para listas aninhadas (1:N)."""
                if incoming_data_list is None:
                    return 
                
                existing_map = {getattr(c, id_field): c for c in existing_children}
                incoming_ids = set()
                
                for data_dict in incoming_data_list:
                    child_id = data_dict.get(id_field)

                    if child_id:
                        incoming_ids.add(child_id)
                        child_to_update = existing_map.get(child_id)
                        if child_to_update:
                            for key, value in data_dict.items():
                                if key != id_field: 
                                    setattr(child_to_update, key, value)
                    else: 
                        data_dict[fk_field] = user_id
                        self.session.add(ChildORM(**data_dict))
                        
                ids_to_delete = existing_map.keys() - incoming_ids
                if ids_to_delete:
                    delete_stmt = delete(ChildORM).where(getattr(ChildORM, id_field).in_(ids_to_delete))
                    self.session.execute(delete_stmt)

            if endereco_data_to_update:
                handle_one_to_many_update(
                    existing_user.endereco,
                    endereco_data_to_update,
                    Endereco, 
                    'id_endereco',
                    'fk_id_user'
                )

            if contato_data_to_update:
                handle_one_to_many_update(
                    existing_user.contatos,
                    contato_data_to_update,
                    Contato, 
                    'id_contato',
                    'fk_id_user'
                )

            if extra_data_to_update:
                user_level = existing_user.lv_acesso
                user_id = existing_user.id_user                 
                def update_one_to_one(existing_rel, update_dict, ORM_Class, fk_field):
                    if existing_rel:
                        for key, value in update_dict.items():
                            setattr(existing_rel, key, value)
                    else:
                        update_dict[fk_field] = user_id
                        self.session.add(ORM_Class(**update_dict))

                if user_level == 'aluno':
                    update_one_to_one(existing_user.estudante, extra_data_to_update, Estudante, 'fk_id_user')

                elif user_level == 'instrutor':
                    update_one_to_one(existing_user.professor, extra_data_to_update, Professor, 'fk_id_user')
                
                elif user_level == 'colaborador':
                    is_recepcionista_update = extra_data_to_update.get('is_recepcionista')

                    if is_recepcionista_update is not None:
                        if existing_user.recepcionista and is_recepcionista_update == False:
                            self.session.delete(existing_user.recepcionista)
                            self.session.add(Administracao(fk_id_user=user_id))
                        
                        elif existing_user.administracao and is_recepcionista_update == True:
                            self.session.delete(existing_user.administracao)
                            self.session.add(Recepcionista(fk_id_user=user_id))
            
            self.session.commit()
            self.session.refresh(existing_user)
            return existing_user

        except SQLAlchemyError as AlchemyError:
            self.session.rollback()
            print(f'Erro de SQLAlchemy ao atualizar usuário no banco:\n{AlchemyError}')
            traceback.print_exc()
            return None
        


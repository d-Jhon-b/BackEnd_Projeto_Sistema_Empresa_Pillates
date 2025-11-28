from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.Instrutor import Professor
from sqlalchemy.orm import joinedload
from typing import Dict, Union, Optional, List
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging 


#para teste:
from src.database.connPostGreNeon import CreateSessionPostGre

class ProfessorModel:
    def __init__(self, db_session:Session):
        self.session = db_session

    def select_all_instructor(self, studio_id:int |None=None)->list[Usuario]:
        try:
            stmt = (
                select(Usuario)
                .join(Professor) 
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.professor)
                )
            )
            if studio_id is not None:
                stmt = stmt.where(Usuario.fk_id_estudio == studio_id)

            resutls = self.session.execute(stmt)
            instructor_list = resutls.scalars().unique().all()
            return instructor_list
        
        except SQLAlchemyError as err:
            logging.error(f'erro ao selecionar todos os alunos:\n{err}')
            return err
    def select_instructor_by_id(self, user_id:int |None = None):
        try:
            # stmt = select(Usuario)
            # stmt = stmt.join(Professor)

            stmt = (
                select(Usuario)
                .join(Professor)
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.professor)
                )
            )
            if user_id is not None:
                stmt = stmt.where(Usuario.id_user == user_id)
            results = self.session.execute(stmt).unique().scalar_one_or_none()
            instructor_value = results
            return instructor_value
        except SQLAlchemyError as err:
            logging.error(f'erro ao buscar aluno:\n{err}')
            return err
        



    def select_id_user_by_fk_id_professor(self, professor_id:int)->Optional[int]:
        try:
            stmt =(
                select(Professor.fk_id_user).join(Usuario).where(Professor.id_professor == professor_id)
            )   
            id_user = self.session.execute(stmt).scalar_one_or_none()        
        # UserValidation.check_self_or_admin_permission
            
            # print(f'{id_user}\n\n\n\n\n')
            return id_user
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar id_user pelo id_estudante: {err}")
            raise err
        except Exception as err:
            logging.error(f"Erro ao buscar id_user pelo id_estudante: {err}")
            raise err
        

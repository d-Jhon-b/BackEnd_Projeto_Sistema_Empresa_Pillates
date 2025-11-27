from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes

from datetime import date
from typing import Dict, Union, Optional, List
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

#para teste
from src.database.connPostGreNeon import CreateSessionPostGre


class AlunoModel:
    def __init__(self, db_session:Session):
        self.session = db_session

    def select_all_students(self, studio_id:int |None = None)->list[Usuario]:
        try:
            stmt = (
                select(Usuario)
                .join(Estudante) 
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.estudante) 
                )
            )
            if studio_id is not None:
                stmt = stmt.where(Usuario.fk_id_estudio == studio_id)

            resutls = self.session.execute(stmt)
            student_list = resutls.scalars().unique().all()
            return student_list
            
        except SQLAlchemyError as err:
            logging.error(f'erro ao selecionar todos os alunos:\n{err}')
            return []
    
    def select_id_user_by_fk_id_estudante(self, estudante_id:int)->Optional[int]:
        try:
            stmt =(
                select(Estudante.fk_id_user).join(Usuario).where(Estudante.id_estudante == estudante_id)
            )   
            id_user = self.session.execute(stmt).scalar_one_or_none()        
        # UserValidation.check_self_or_admin_permission
            return id_user
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar id_user pelo id_estudante: {err}")
            raise err
        except Exception as err:
            logging.error(f"Erro ao buscar id_user pelo id_estudante: {err}")
            raise err

    def select_student_by_id(self, user_id:int |None = None):
        try:
            stmt = (
            select(Usuario)
            .join(Estudante)
            .options(
                joinedload(Usuario.endereco),
                joinedload(Usuario.contatos),
                joinedload(Usuario.estudante)
            )
            )
            if user_id is not None:
                stmt = stmt.where(Usuario.id_user == user_id)
            results = self.session.execute(stmt).unique().scalar_one_or_none()
            student_value = results
            
            return student_value
        except SQLAlchemyError as err:
            logging.error(f'erro ao buscar aluno:\n{err}')
            return err


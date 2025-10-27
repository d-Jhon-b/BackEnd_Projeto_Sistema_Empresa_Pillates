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
        

# session_create = CreateSessionPostGre()
# get_db = session_create.get_session()

# try:
#     alunoTest = ProfessorModel(db_session=get_db)
#     aluno_select = alunoTest.select_all_insttructor(1)
#     for a in aluno_select:
#         print(a)

#     aluno_select_id = alunoTest.select_instructor_by_id(1)
#     print(aluno_select_id)
# except Exception as err:
#     print(err)
#     get_db.close()
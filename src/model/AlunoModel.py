from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante

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


# session_create = CreateSessionPostGre()
# db_session = session_create.get_session()
# try:
#     aluno_teste = AlunoModel(db_session=db_session)
#     aluno_select_all = aluno_teste.select_all_students(studio_id=1)
#     for a in aluno_select_all:
#         print(a) 
#     # aluno_select_one = aluno_teste.select_student_by_id(user_id=1004)
#     # print(aluno_select_one)
# except SQLAlchemyError as err:
#     print(err)

# try:
#     aluno_test = AlunoModel(db_session=db_session)
#     # aluno_select_all = aluno_test.select_all_students(studio_id=1)
#     # for a in aluno_select_all:
#     #     print(a) 
#     aluno_select_one = aluno_test.select_student_by_id(user_id=1)
#     print(aluno_select_one)

# except Exception as err:
#     print(f"\nErro fatal ao iniciar a sessão ou rodar testes: {err}")
# finally:
#     db_session.close()
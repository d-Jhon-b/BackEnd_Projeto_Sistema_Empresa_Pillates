from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, insert, delete, update, func
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any

from src.model.aulaModel.aulaConfig import Aula, Estudante_Aula
from src.database.connPostGreNeon import CreateSessionPostGre
# from src.model.aulaModel.aulaConfig import Aula


class NumAlunosValidation:
    @staticmethod
    def num_max_alunos(db_session:Session, aula_id:int)->bool:
        try:
            stmt = select(func.count(Estudante_Aula.fk_id_estudante)).where(
                Estudante_Aula.fk_id_aula == aula_id
            )
            total_alunos = db_session.execute(stmt).scalar_one()

            if total_alunos >= 3:
                print(f"Aula {aula_id} já atingiu o limite de 3 alunos (atual: {total_alunos}).")
                return False
            
            return True
        except SQLAlchemyError as err:
            print('Não foi possivel inserir usuario, número máximo de alunos matriculado')
            return False
        except Exception as err:
            print('Erro ao validar numero de alunos')
            return False
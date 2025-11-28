from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, insert, delete, update, func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
#importa classes do pydantic 
from typing import List, Optional, Dict, Any

#importando classes das tabelas de config
from src.model.aulaModel.aulaConfig import Aula, Estudante_Aula
from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.database.connPostGreNeon import CreateSessionPostGre
from src.model.userModel.typeUser.Instrutor import Professor
from src.model.aulaModel.validations.num_estudantes import NumAlunosValidation
import logging

class AulaModel:
    def __init__(self, db_session: Session):
        self.session = db_session

    # def select_my_aulas(self, user_id)->Optional [Aula]:
    #     stmt = (
    #         select(Aula).where(Aula.fk)
    #     )
    def select_aula_by_id(self, aula_id: int) -> Optional[Aula]:
        """Seleciona uma aula pelo ID, carregando estudantes (N:N)."""
        stmt = (
            select(Aula)
            .where(Aula.id_aula == aula_id)
            .options(joinedload(Aula.estudantes_associacao)) 
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def select_all_aulas(self, studio_id: Optional[int] = None) -> List[Aula]:
        """Lista todas as aulas, opcionalmente filtrando por estúdio."""
        stmt = select(Aula).options(joinedload(Aula.estudantes_associacao))
        
        if studio_id is not None:
            stmt = stmt.where(Aula.fk_id_estudio == studio_id)
        
        return self.session.execute(stmt).scalars().unique().all()


    def insert_new_aula(self, aula_data: Dict[str, Any], estudantes_ids: Optional[List[int]]) -> Aula:
        """Insere uma nova aula e matricula estudantes iniciais (recebe dict)."""
        try:
            new_aula = Aula(**aula_data)
            self.session.add(new_aula)
            self.session.flush()
            if estudantes_ids:
                for estudante_id in estudantes_ids:
                    # 'normal' é o valor padrão do Enum
                    matricula = Estudante_Aula(
                        fk_id_estudante=estudante_id,
                        fk_id_aula=new_aula.id_aula,
                        tipo_de_aula='normal' 
                    )
                    self.session.add(matricula)
            
            self.session.commit()
            self.session.refresh(new_aula)
            return new_aula
        except SQLAlchemyError:
            self.session.rollback()
            raise


    def update_aula_data(self, aula_id: int, data_to_update: Dict[str, Any]) -> Optional[Aula]:
        """Atualiza os dados de uma aula existente (recebe dict)."""
        try:
            existing_aula = self.session.get(Aula, aula_id)
            if not existing_aula:
                return None
            
            for key, value in data_to_update.items():
                setattr(existing_aula, key, value)
            
            self.session.commit()
            self.session.refresh(existing_aula)
            return existing_aula
        except SQLAlchemyError:
            self.session.rollback()
            raise


    def delete_aula_by_id(self, aula_id: int) -> bool:
        """Deleta uma aula pelo ID."""
        try:
            # result = self.session.execute(delete(Aula).where(Aula.id_aula == aula_id))
            # self.session.commit()
            # return result.rowcount > 0

            """
            delete = Deletar registro
            (Estudante_Aula) = Com base na tabela Estudante_Aula (Schema encontrado em src.model.aulaModel.Aula_config na classe Estudante_Aula)
            where = Onde 
            (Estudante_Aula.fk_id_aula == aula_id)= Na tabela Estudante_Aula tenha o fk_id_aula == aula_id enviado para o método como parametro  
            """
            delete_matriculas_stmt = delete(Estudante_Aula).where(Estudante_Aula.fk_id_aula == aula_id)
            
            """
            Execute= função do SQLAlchemy para aplicar uma alteração no banco (PostGre) 
            """
            self.session.execute(delete_matriculas_stmt)

            """Delete a aula com base no (Schema da aula) com base no id_de_aula """            
            delete_aula_stmt = delete(Aula).where(Aula.id_aula == aula_id)
            result = self.session.execute(delete_aula_stmt)            
            self.session.commit()
            """
            Faz um contador para verificar que o número de linhas escontrados seja superios a 0, o que significa que houve um exclusão
            """
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            raise
    


    # --- Métodos para Matrícula (N:N) ---
    
    def enroll_student(self, aula_id: int, matricula_data: Dict[str, Any]) -> Estudante_Aula:
        """Matricula um estudante em uma aula (recebe dict)."""
        try:
            result_validation = NumAlunosValidation.num_max_alunos(self.session, aula_id=aula_id)
            if not result_validation:
                raise ValueError(f"A aula {aula_id} já atingiu o número máximo de alunos (3).")

            enrollment = Estudante_Aula(fk_id_aula=aula_id, **matricula_data)
            self.session.add(enrollment)
            self.session.commit()
            self.session.refresh(enrollment)
            return enrollment
        except SQLAlchemyError as err:
            print(f'Erro ao aplicar aluno na aula {err}')
            self.session.rollback()
            raise

    # def select_my_aulas(self, user_id: int, is_instructor: bool = False) -> List[int]:
    #     if is_instructor:
    #         stmt = select(Aula.id_aula).where(
    #             (Aula.fk_id_professor == user_id) | (Aula.fk_id_professor_substituto == user_id)
    #         )
    #     else:
    #         stmt = select(Estudante_Aula.fk_id_aula).where(
    #             Estudante_Aula.fk_id_estudante == user_id
    #         )
            
    #     return self.session.execute(stmt).scalars().all()

    def select_my_aulas(self, user_id: int, is_instructor: bool = False) -> List[int]:
        # print(f'{is_instructor}\n\n\n\n')
        if is_instructor:
            try:
                stmt_professor = select(Professor.id_professor).where(Professor.fk_id_user == user_id)
                professor_id = self.session.execute(stmt_professor).scalar_one_or_none()
                print(professor_id)
            except NameError:
                raise RuntimeError("Modelo 'Professor' não encontrado para mapeamento de ID.")

            if professor_id is None:
                return [] 
                
            stmt = select(Aula.id_aula).where(
                (Aula.fk_id_professor == professor_id) | (Aula.fk_id_professor_substituto == professor_id)
            )
            
        else: 
            try:
                stmt_estudante = select(Estudante.id_estudante).where(Estudante.fk_id_user == user_id)
                estudante_id = self.session.execute(stmt_estudante).scalar_one_or_none()
            except NameError:
                raise RuntimeError("Modelo 'Estudante' não encontrado para mapeamento de ID.")
            
            if estudante_id is None:
                return [] 
                
            stmt = select(Estudante_Aula.fk_id_aula).where(
                Estudante_Aula.fk_id_estudante == estudante_id
            )
            
        return self.session.execute(stmt).scalars().all()

    def count_future_enrollments(self, estudante_id: int) -> int:
        current_datetime = datetime.now()
        stmt = select(func.count(Estudante_Aula.fk_id_aula)).join(Aula).where(
            Estudante_Aula.fk_id_estudante == estudante_id,
            Aula.data_aula > current_datetime
        )
        
        count = self.session.execute(stmt).scalar_one()
        
        return count if count is not None else 0
        




        #----------adicionado para tirar um aluno da aula, mas não aplicado de froma exata
    def unenroll_student(self, aula_id: int, estudante_id: int) -> bool:
        try:
            stmt = delete(Estudante_Aula).where(
                (Estudante_Aula.fk_id_aula == aula_id) & 
                (Estudante_Aula.fk_id_estudante == estudante_id)
            )
            result = self.session.execute(stmt)
            self.session.commit()
            
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            raise
    #------------------não aplicado para produto final


#     def select_aluno_aula_by_professor_id(self, professor_id):
#         try:
#             stmt = select(Aula.id_aula).where(Aula.fk_id_professor == professor_id)
#             id_aula_resultado = self.session.execute(stmt).unique().all()

#             logging.error(f'{id_aula_resultado}')
#             print(f'{id_aula_resultado}\n\n\n')

#             return id_aula_resultado
#         except SQLAlchemyError as err:
#             logging.error(f'Erro ao buscar aula com base no professor: \n{err}')
#             return None
#         except Exception as err:
#             logging.error(f'Erro ao processar busca de aula com base no professor: \n{err}')
#             return None
        

# create_seesion = CreateSessionPostGre()
# session = create_seesion.get_session()
# aula_model = AulaModel(db_session=session)

# try:
#     id_sensei = 1
#     res = aula_model.select_aluno_aula_by_professor_id(professor_id=id_sensei)
#     print(res)


# except SQLAlchemyError as err:
#     print(err)

# except Exception as err:
#     print(err)

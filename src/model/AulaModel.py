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
        if is_instructor:
            try:
                stmt_professor = select(Professor.id_professor).where(Professor.fk_id_user == user_id)
                professor_id = self.session.execute(stmt_professor).scalar_one_or_none()
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
        




        #----------adicionado para, mas não aplicado de froma exata
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


# create_session = CreateSessionPostGre()
# session = create_session.get_session()
# aula_model = AulaModel(session)
# import logging
# try:
#     user_id=1
#     estudante_id=False

#     my_class = aula_model.select_my_aulas(1)
#     for i in my_class:
#         print(i)    
# except Exception as err:
#     logging.error(f'{err}')
#     print(err)

# from datetime import datetime
# from src.model.userModel.typeUser.aluno import Estudante
# from src.model.UserModel import UserModel
# create_session=CreateSessionPostGre()
# session = create_session.get_session()
# aula_model=AulaModel(db_session=session)

# MOCK_FK_PROFESSOR = 1 
# MOCK_FK_ESTUDIO = 1
# TITULO_DA_AULA = f"Teste de Inserção {datetime.now().strftime('%Y%m%d%H%M%S')}"
# MOCK_DATA_AULA = datetime(2026, 12, 25, 10, 0, 0) # Exemplo de data futura
# MOCK_DESC = "Aula criada via teste de integracao do Model."

# aula_data_sql = {
#     "fk_id_professor": MOCK_FK_PROFESSOR,
#     "fk_id_estudio": MOCK_FK_ESTUDIO,
#     "data_aula": MOCK_DATA_AULA,
#     "titulo_aula": TITULO_DA_AULA,
#     "desc_aula": MOCK_DESC
# }

# estudantes_ids = [2, 3] 

# try:
#     print(f"\n--- Iniciando Teste de Inserção SQL Real ---")
#     print(f"Dados: {aula_data_sql}")
    
#     new_aula_orm = aula_model.insert_new_aula(
#         aula_data=aula_data_sql,
#         estudantes_ids=estudantes_ids
#     )

#     print(f"ID da Aula: {new_aula_orm.id_aula}")
#     print(f"Título: {new_aula_orm.titulo_aula}")
#     print(f"Matrículas: {[ea.fk_id_estudante for ea in new_aula_orm.estudantes_associacao]}")

# except SQLAlchemyError as e:
#     print(f"Detalhes: {e}")
# except Exception as e:
#     print(f"Erro Inesperado: {e}")
    



# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.database.connPostGreNeon import CreateSessionPostGre
    


# try:
#     create_session = CreateSessionPostGre()
#     db_session = create_session.get_session()
    
#     # Assumindo que sua classe AulaModel se chama 'AulaModel'
#     aula_model = AulaModel(db_session=db_session) 
    
#     ID_ESTUDANTE = 1 # O mesmo estudante que tem 4 aulas restantes
    
#     aulas_futuras = aula_model.count_future_enrollments(ID_ESTUDANTE)
#     print(f"Estudante {ID_ESTUDANTE} tem {aulas_futuras} aulas futuras matriculadas.")
    
#     # AQUI ESTÁ A CHAVE: Se aulas_futuras for 4, 5, etc., o erro 400 é esperado.
#     # Se for 0 ou 1, o erro 400 é INESPERADO.
#     if aulas_futuras >= 4:
#         print("AVISO CRÍTICO: Matrículas futuras consomem todo o saldo restante (4).")
        
# except Exception as e:
#     print(f"ERRO INESPERADO no teste do AulaModel: {e}")
# finally:
#     if 'db_session' in locals():
#         db_session.close()
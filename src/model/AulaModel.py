from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any

# Importar classes ORM
from src.model.aulaModel.aulaConfig import Aula, Estudante_Aula
from src.database.connPostGreNeon import CreateSessionPostGre

class AulaModel:
    def __init__(self, db_session: Session):
        self.session = db_session

    # def select_my_aulas(self, user_id)->Optional [Aula]:
    #     stmt = (
    #         select(Aula).where(Aula.fk)
    #     )
    def select_aula_by_id(self, aula_id: int) -> Optional[Aula]:
        """Seleciona uma aula pelo ID, carregando estudantes (N:N)."""
        # Carregando a associação N:N (estudantes_associacao)
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
            self.session.flush() # Obtém o ID da aula

            # Matrícula inicial, se houver estudantes
            if estudantes_ids:
                for estudante_id in estudantes_ids:
                    # 'normal' é o valor padrão no seu Enum
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
            # O ORM cascade deve cuidar das matrículas em Estudante_Aula
            result = self.session.execute(delete(Aula).where(Aula.id_aula == aula_id))
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            raise
    
    # --- Métodos para Matrícula (N:N) ---
    
    def enroll_student(self, aula_id: int, matricula_data: Dict[str, Any]) -> Estudante_Aula:
        """Matricula um estudante em uma aula (recebe dict)."""
        try:
            enrollment = Estudante_Aula(fk_id_aula=aula_id, **matricula_data)
            self.session.add(enrollment)
            self.session.commit()
            self.session.refresh(enrollment)
            return enrollment
        except SQLAlchemyError:
            self.session.rollback()
            raise



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
    
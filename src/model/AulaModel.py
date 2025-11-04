from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any

# Importar classes ORM
from src.model.aulaModel.aulaConfig import Aula, Estudante_Aula


class AulaModel:
    def __init__(self, db_session: Session):
        self.session = db_session

    def select_aula_by_id(self, aula_id: int) -> Optional[Aula]:
        """Seleciona uma aula pelo ID, carregando estudantes (N:N)."""
        # Carregando a associação N:N (estudantes_associacao)
        stmt = (
            select(Aula)
            .where(Aula.id_aula == aula_id)
            .options(joinedload(Aula.estudantes_associacao)) 
        )
        return self.session.execute(stmt).scalar_one_or_none()

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
from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.schemas.planos_personalizados_schemas import PlanoPersonalizadoCreate, PlanoPersonalizadoUpdate 

class PlanosPersonalizadosModel:
    """DAO para operações CRUD na tabela Planos Personalizados."""

    def __init__(self, session_db: Session):
        self.session = session_db

    def insert_new_plano(self, data_to_insert: PlanoPersonalizadoCreate) -> PlanosPersonalizados:
        """Insere um novo Plano Personalizado."""
        try:
            plano_data_dict: Dict[str, Any] = data_to_insert.model_dump(exclude_defaults=False)
            
            new_plano = PlanosPersonalizados(**plano_data_dict)
            self.session.add(new_plano)
            self.session.commit()
            self.session.refresh(new_plano)
            return new_plano
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Falha de integridade ao criar Plano Personalizado: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao criar Plano Personalizado: {e}")

    def update_plano_data(self, plano_id: int, data_to_update: PlanoPersonalizadoUpdate) -> Optional[PlanosPersonalizados]:
        """Atualiza um Plano Personalizado existente pelo ID."""

        update_dict: Dict[str, Any] = data_to_update.model_dump(exclude_unset=True)
        
        if not update_dict:
            return self.session.get(PlanosPersonalizados, plano_id)
            
        try:
            existing_plano = self.session.get(PlanosPersonalizados, plano_id)
            if not existing_plano:
                return None
            
            for key, value in update_dict.items():
                setattr(existing_plano, key, value)
            
            self.session.commit()
            self.session.refresh(existing_plano)
            return existing_plano
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao atualizar Plano Personalizado: {e}")

    def select_plano_by_id(self, plano_id: int) -> Optional[PlanosPersonalizados]:
        """Busca um Plano Personalizado pelo ID."""
        try:
            return self.session.get(PlanosPersonalizados, plano_id)
        except SQLAlchemyError:
            return None

    def select_all_planos(self) -> List[PlanosPersonalizados]:
        """Lista todos os Planos Personalizados."""
        try:
            stmt = select(PlanosPersonalizados)
            return self.session.execute(stmt).scalars().all()
        except SQLAlchemyError:
            return []

    def delete_plano_by_id(self, plano_id: int) -> bool:
        """Deleta um Plano Personalizado pelo ID."""
        try:
            delete_stmt = delete(PlanosPersonalizados).where(PlanosPersonalizados.id_plano_personalizado == plano_id)
            result = self.session.execute(delete_stmt)
            self.session.commit()
            return result.rowcount > 0
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Não foi possível deletar o Plano Personalizado. Existem contratos vinculados: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao deletar Plano Personalizado: {e}")
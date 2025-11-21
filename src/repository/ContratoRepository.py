from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

from src.model.planosModel.contratoConfig import Contrato # Assumindo que Contrato tem um campo 'aulas_restantes'
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano

class ContratoRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def _get_active_contract(self, estudante_id: int) -> Optional[Contrato]:
        """Busca o contrato ativo principal para o estudante."""
        # A lógica real pode ser mais complexa (validade, tipo, prioridade), mas simplificamos:
        stmt = select(Contrato).join(AdesaoPlano).where(
            and_(
                AdesaoPlano.fk_id_estudante == estudante_id,
                Contrato.status == 'ativo', # Condição real de contrato ativo
            )
        ).order_by(Contrato.data_inicio.desc())
        
        return self.session.execute(stmt).scalar_one_or_none()

    
    def debitar_aula_do_plano(self, estudante_id: int) -> bool: 
        contrato = None 
        try:
            contrato: Optional[Contrato] = self._get_active_contract(estudante_id)

            if not contrato:
                raise ValueError(f"Estudante {estudante_id} não possui contrato ativo para débito.")

            if contrato.aulas_restantes <= 0:
                raise ValueError(f"Contrato ID {contrato.id_contrato} não tem saldo de aulas restante.")
            
            update_stmt = (
                update(Contrato)
                .where(Contrato.id_contrato == contrato.id_contrato)
                .values(aulas_restantes=Contrato.aulas_restantes - 1)
            )
            
            self.session.execute(update_stmt)
            self.session.commit()
            
            logging.info(f"Débito: 1 aula consumida. Estudante {estudante_id}. Contrato ID: {contrato.id_contrato}")
            return True
            
        except ValueError:
            raise 
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"Erro SQL ao debitar aula do plano: {e}")
            raise # Repassa o erro SQL para o Controller
        
        # Em caso de qualquer outro erro não tratado, o finally faz o rollback
        except Exception as e:
            self.session.rollback()
            raise e
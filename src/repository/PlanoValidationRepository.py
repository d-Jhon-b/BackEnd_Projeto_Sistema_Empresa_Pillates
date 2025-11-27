from sqlalchemy.orm import Session
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.contratoConfig import Contrato 
from src.model.AdesaoPlanoModel import AdesaoPlanoModel 
from src.model.PlanoModel import PlanosModel 
from src.model.PlanosCustomizadosModel import PlanosPersonalizadosModel 

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
import logging

class PlanoValidationRepository:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.adesao_model = AdesaoPlanoModel(db_session)
        self.plano_model = PlanosModel(db_session)
        self.plano_personalizado_model = PlanosPersonalizadosModel(db_session)

    def _get_active_contract(self, adesao_id: int) -> Optional[Contrato]:
        try:
            stmt = select(Contrato).where(
                and_(
                    Contrato.fk_id_adesao_plano == adesao_id,
                )
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            logging.error(f"Erro ao buscar contrato ativo para adesão {adesao_id}: {e}")
            return None


    def is_student_eligible_for_enrollment(self, estudante_id: int, aula_id: int) -> bool:
        active_adesoes: List[AdesaoPlano] = self.adesao_model.select_active_adesao_by_estudante_id(estudante_id)
        
        if not active_adesoes:
            raise ValueError("O estudante não possui nenhuma adesão de plano ativa e válida no momento.")
        
        for adesao in active_adesoes:
            contrato = self._get_active_contract(adesao.id_adesao_plano)
            if contrato:
                return True
                
        raise ValueError("O estudante não está elegível para matrícula. Plano ativo não encontrado ou contrato pendente/expirado.")
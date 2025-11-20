# src.controllers.validations/AdesaoValidation.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload
from typing import Dict, Any

class AdesaoValidation:
    
    @staticmethod
    def _check_no_active_plan(session_db: Session, estudante_id: int):
        """
        Verifica se o estudante já possui uma adesão de plano ATIVA (válida).
        Se encontrar uma adesão ativa, levanta HTTPException.
        """
        adesao_plano_model = AdesaoPlanoModel(session_db=session_db)
        
        active_plans = adesao_plano_model.select_active_adesao_by_estudante_id(estudante_id)
        
        if active_plans:
            # Pega o ID da primeira adesão ativa encontrada para a mensagem de erro
            active_id = active_plans[0].id_adesao_plano 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"O estudante ID {estudante_id} já possui um plano ATIVO (Adesão ID: {active_id}). "
                    "Para trocar de plano, o plano atual deve expirar ou ser desativado."
                )
            )

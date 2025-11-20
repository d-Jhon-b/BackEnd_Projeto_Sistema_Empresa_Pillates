from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.AdesaoPlanoModel import AdesaoPlanoModel

class ContratoValidation:
    
    @staticmethod
    def _check_adesao_contract_status(session_db: Session, adesao_id: int):
        adesao_repo = AdesaoPlanoModel(session_db=session_db)
        contrato_db = adesao_repo._get_contrato_by_adesao_id(adesao_id)
        
        if contrato_db is None:
            return 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A Adesão ID {adesao_id} já possui um contrato formalizado (Contrato ID: {contrato_db.id_contrato})."
        )
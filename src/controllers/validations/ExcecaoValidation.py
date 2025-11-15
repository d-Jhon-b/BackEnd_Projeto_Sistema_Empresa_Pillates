from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from src.model.EstudioModel import EstudioModel 

class ExcecaoValidation:
    
    @staticmethod
    def _check_estudio_exists(db_session: Session, estudio_id: int):
        """ Verifica se o estúdio FK existe no SQL. """
        estudio_repo = EstudioModel(db_session=db_session)
        if not estudio_repo.check_exists_by_id(estudio_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estúdio com ID {estudio_id} não encontrado."
            )
            
    @staticmethod
    def _check_date_range(start_date: date, end_date: date):
        """ Verifica a lógica básica do período de busca. """
        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A data de início deve ser anterior à data de fim."
            )
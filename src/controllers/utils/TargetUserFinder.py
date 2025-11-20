from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.model.AlunoModel import AlunoModel
from src.controllers.validations.permissionValidation import UserValidation


class TargetUserFinder:

    @staticmethod
    def check_and_get_target_user_id(
        session_db: Session, 
        estudante_id: int, 
        current_user: Dict[str, Any]
    ) -> int:

        estudante_model = AlunoModel(db_session=session_db)
        target_user_id = estudante_model.select_id_user_by_fk_id_estudante(estudante_id)
        
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Estudante ID {estudante_id} não encontrado ou sem usuário associado."
            )
            
        UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        return target_user_id
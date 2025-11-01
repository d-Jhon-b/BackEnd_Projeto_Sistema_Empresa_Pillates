# src/controllers/estudioController.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.EstudioModel import EstudioModel 
from src.schemas.estudio_schemas import EstudioCreateSchema, EstudioResponseSchema, EstudioUpdateSchema
from typing import List, Optional, Dict, Any
from src.controllers.validations.permissionValidation import UserValidation

# NOTE: Assumindo que você tem classes de validação e operações de utilidade
# from src.controllers.validations.permissionValidation import UserValidation 
from src.controllers.operations.operations import Operations 

class EstudioController:
    def _get_repo(self, db_session: Session) -> EstudioModel:
        return EstudioModel(db_session=db_session)

    def create_estudio(self, estudio_data: EstudioCreateSchema, current_user: Dict[str, Any], db_session: Session) -> EstudioResponseSchema:
        UserValidation._check_admin_permission(current_user) # Exemplo de validação de permissão
        try:
            estudio_repo = self._get_repo(db_session)
            new_estudio_db = estudio_repo.create_estudio(estudio_data)
            return EstudioResponseSchema.model_validate(new_estudio_db)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao criar Estúdio: {e}"
            )

    def get_estudio_by_id(self, estudio_id: int, current_user: Dict[str, Any], db_session: Session) -> EstudioResponseSchema:
        UserValidation._check_admin_permission(current_user)
        estudio_repo = self._get_repo(db_session)
        estudio_db = estudio_repo.select_estudio_by_id(estudio_id)
        
        if not estudio_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estúdio com ID {estudio_id} não encontrado."
            )
        return EstudioResponseSchema.model_validate(estudio_db)

    def get_all_estudios(self, current_user: Dict[str, Any], db_session: Session) -> List[EstudioResponseSchema]:
        UserValidation._check_admin_permission(current_user) # Exemplo de validação de permissão
        estudio_repo = self._get_repo(db_session)
        estudios_db = estudio_repo.select_all_estudios()
        return [EstudioResponseSchema.model_validate(e) for e in estudios_db]

    def update_estudio(self, estudio_id: int, update_data: EstudioUpdateSchema, current_user: Dict[str, Any], db_session: Session) -> EstudioResponseSchema:
        UserValidation._check_admin_permission(current_user) # Exemplo de validação de permissão

        if not update_data.model_dump(by_alias=True, exclude_none=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo fornecido para atualização."
            )
        
        try:
            estudio_repo = self._get_repo(db_session)
            updated_estudio_db = estudio_repo.update_estudio(estudio_id, update_data)
            
            if not updated_estudio_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Estúdio com ID {estudio_id} não encontrado."
                )
            return EstudioResponseSchema.model_validate(updated_estudio_db)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao atualizar Estúdio: {e}"
            )
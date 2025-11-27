from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Dict, Any

from src.model.PlanoModel import PlanosModel 

from src.schemas.plano_schemas import (PlanoCreate, PlanoResponse, PlanoUpdate)

from src.controllers.validations.permissionValidation import UserValidation


class PlanosController:
    def create_plano_padrao(self, session_db: Session, data_plano: PlanoCreate, current_user: Dict[str, Any]) -> PlanoResponse:
        UserValidation._check_admin_permission(current_user)
        try:
            
            plano_repo = PlanosModel(session_db=session_db) 
            new_plano = plano_repo.insert_new_plano(data_plano)
            return PlanoResponse.model_validate(new_plano)
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Falha de integridade: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao criar Plano Padrão: {e}"
            )

    def get_all_planos_padrao(self, session_db: Session, current_user: Dict[str, Any]) -> List[PlanoResponse]:
        UserValidation._check_all_permission(current_user) 
        try:
            
            plano_repo = PlanosModel(session_db=session_db) 
            planos_db = plano_repo.select_all_planos()
            return [PlanoResponse.model_validate(plano) for plano in planos_db]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha ao buscar Planos Padrão: {e}"
            )
            
    def get_plano_padrao_by_id(self, plano_id: int, session_db: Session, current_user: Dict[str, Any]) -> PlanoResponse:
        UserValidation._check_all_permission(current_user) 
        try:
            plano_repo = PlanosModel(session_db=session_db)
            plano_db = plano_repo.select_plano_by_id(plano_id)
            if not plano_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plano Padrão com ID {plano_id} não encontrado."
                )
            return PlanoResponse.model_validate(plano_db)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha ao buscar PLano Padrão: {e}"
            )


    def update_plano_padrao(self, plano_id: int, session_db: Session, data_update: PlanoUpdate, current_user: Dict[str, Any]) -> PlanoResponse:
        UserValidation._check_admin_permission(current_user)

        if not data_update.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo fornecido para atualização parcial."
            )

        try:
            
            plano_repo = PlanosModel(session_db=session_db) 
            updated_plano = plano_repo.update_plano_data(plano_id, data_update)

            if not updated_plano:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plano Padrão com ID {plano_id} não encontrado."
                )
            return PlanoResponse.model_validate(updated_plano)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao atualizar Plano Padrão: {e}"
            )

    def delete_plano_padrao(self, plano_id: int, session_db: Session, current_user: Dict[str, Any]):
        UserValidation._check_admin_permission(current_user)
        try:
            
            plano_repo = PlanosModel(session_db=session_db) 
            deleted = plano_repo.delete_plano_by_id(plano_id)
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plano Padrão com ID {plano_id} não encontrado."
                )
            return {"message": f"Plano Padrão com ID {plano_id} deletado com sucesso."}
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Não é possível deletar o plano: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao deletar Plano Padrão: {e}"
            )
            
 
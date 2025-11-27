from fastapi import HTTPException, status
from sqlalchemy.orm import Session 
from typing import Dict, Any, List, Optional
from datetime import date # Novo import necessário
from src.schemas.excecao_schemas import ExcecaoCreateSchema, ExcecaoResponseSchema, ExcecaoUpdateSchema # Novo import
from src.model.agendaModel.excecaoRepository import ExcecaoRepository
from src.model.EstudioModel import EstudioModel 
from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.validations.ExcecaoValidation import ExcecaoValidation


class ExcecaoController:
    
    def __init__(self, excecao_repo: ExcecaoRepository):
        self.excecao_repo = excecao_repo

    async def create_excecao(
        self, 
        excecao_data: ExcecaoCreateSchema, 
        current_user: Dict[str, Any],
        db_session_sql: Session 
    ) -> ExcecaoResponseSchema:
        
        UserValidation._check_admin_permission(current_user)
        estudio_id = excecao_data.fk_id_estudio
        ExcecaoValidation._check_estudio_exists(db_session_sql, estudio_id)

        data_to_insert = excecao_data.model_dump(by_alias=True)
        new_id = await self.excecao_repo.insert_excecao(data_to_insert)

        created_doc = await self.excecao_repo.collection.find_one({"_id": new_id})
        
        return ExcecaoResponseSchema.model_validate(created_doc)
    

    async def get_excecoes_by_period(
        self, 
        start_date: date, 
        end_date: date, 
        estudio_id: Optional[int],
        current_user: Dict[str, Any],
        db_session_sql: Session
    ) -> List[ExcecaoResponseSchema]:
        """ Retorna exceções ativas dentro de um período e, opcionalmente, por estúdio. """
        
        UserValidation._check_all_permission(current_user=current_user)

        if estudio_id is not None:
            ExcecaoValidation._check_estudio_exists(db_session_sql, estudio_id)

        excecoes_data = await self.excecao_repo.find_excecoes_by_period(start_date, end_date, estudio_id)
        
        return [ExcecaoResponseSchema.model_validate(excecao) for excecao in excecoes_data]


    async def update_excecao(
        self, 
        excecao_id: str, 
        update_data: ExcecaoUpdateSchema, 
        current_user: Dict[str, Any],
        db_session_sql: Session
    ) -> ExcecaoResponseSchema:
        
        UserValidation._check_admin_permission(current_user) 
        
        data_to_update = update_data.model_dump(by_alias=True, exclude_none=True)

        if not data_to_update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo fornecido para atualização."
            )

        updated_doc = await self.excecao_repo.update_excecao(excecao_id, data_to_update)
        
        if not updated_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exceção com ID {excecao_id} não encontrada ou não foi alterada."
            )
            
        return ExcecaoResponseSchema.model_validate(updated_doc)
    


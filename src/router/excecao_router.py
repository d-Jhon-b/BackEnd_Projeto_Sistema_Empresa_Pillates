from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date

from src.controllers.excecao_controller import ExcecaoController
from src.schemas.excecao_schemas import ExcecaoCreateSchema, ExcecaoResponseSchema, ExcecaoUpdateSchema

from src.database.connMongo import MongoConnectionManager 
from src.model.agendaModel.excecaoRepository import ExcecaoRepository
from src.database.dependencies import get_db 
from src.utils.authUtils import auth_manager 


router = APIRouter(
    prefix="/cronograma/excecoes",
    tags=["Gestão de Exceções de Cronograma (Folgas/Indisponibilidade)"]
)
def get_excecao_controller_dependency() -> ExcecaoController:
    try:
        mongo_client = MongoConnectionManager.get_client()
    except HTTPException:
        raise 
    mongo_db = mongo_client.get_database(MongoConnectionManager.DB_NAME)
    collection = mongo_db.get_collection("excecoes_cronograma") # Nome da sua Collection

    excecao_repo = ExcecaoRepository(collection)
    return ExcecaoController(excecao_repo)

@router.post(
    "/",
    response_model=ExcecaoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registra um dia de folga/indisponibilidade."
)
async def create_excecao_router(
    excecao_data: ExcecaoCreateSchema,
    db_session: Session = Depends(get_db), 
    current_user: Dict[str, Any] = Depends(auth_manager),
    controller: ExcecaoController = Depends(get_excecao_controller_dependency) 
):
    return await controller.create_excecao(
        excecao_data=excecao_data, 
        current_user=current_user, 
        db_session_sql=db_session
    )


@router.get(
    "/",
    response_model=List[ExcecaoResponseSchema],
    summary="Lista as exceções ATIVAS (dias de folga) por período e estúdio."
)
async def get_excecoes_router(
    start_date: date = Query(..., description="Data de início do período (YYYY-MM-DD)."),
    end_date: date = Query(..., description="Data de fim do período (YYYY-MM-DD)."),
    estudio_id: Optional[int] = Query(None, description="ID do estúdio para filtrar."),
    db_session: Session = Depends(get_db), 
    current_user: Dict[str, Any] = Depends(auth_manager),
    controller: ExcecaoController = Depends(get_excecao_controller_dependency)
):
    # if start_date >= end_date:
    #      raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="A data de início deve ser anterior à data de fim."
    #     )
    # my_user_id = current_user.get("id_user")
    return await controller.get_excecoes_by_period(
        start_date=start_date, 
        end_date=end_date, 
        estudio_id=estudio_id,
        current_user=current_user,
        db_session_sql=db_session
    )


@router.patch(
    "/{excecao_id}",
    response_model=ExcecaoResponseSchema,
    summary="Atualiza descrição ou reverte/reabre uma exceção de cronograma."
)
async def update_excecao_route(
    excecao_id: str,
    update_data: ExcecaoUpdateSchema,
    db_session: Session = Depends(get_db), 
    current_user: Dict[str, Any] = Depends(auth_manager),
    controller: ExcecaoController = Depends(get_excecao_controller_dependency)
):
    if not update_data.model_dump(by_alias=True, exclude_none=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo fornecido para atualização."
        )
    
    return await controller.update_excecao(
        excecao_id=excecao_id, 
        update_data=update_data, 
        current_user=current_user,
        db_session_sql=db_session
    )
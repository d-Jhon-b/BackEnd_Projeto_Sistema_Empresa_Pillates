from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.controllers.estudio_controller import EstudioController
from src.schemas.estudio_schemas import EstudioCreateSchema, EstudioResponseSchema, EstudioUpdateSchema
from src.database.dependencies import get_db 
from src.utils.authUtils import auth_manager # Importe sua função de autenticação

router = APIRouter(
    prefix="/estudios",
    tags=["Gestão de Estúdios"]
)

estudio_controller = EstudioController() 

@router.post(
    "/",
    response_model=EstudioResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo estúdio. (Requer permissão de Admin)"
)
def create_estudio_route(
    estudio_data: EstudioCreateSchema,
    db_session: Session = Depends(get_db), 
    current_user: dict = Depends(auth_manager)
):
    return estudio_controller.create_estudio(
        estudio_data=estudio_data, 
        current_user=current_user, 
        db_session=db_session
    ) 

@router.get(
    "/",
    response_model=List[EstudioResponseSchema],
    summary="Lista todos os estúdios. (Requer permissão de Admin)"
)
def get_all_estudios_route(
    db_session: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return estudio_controller.get_all_estudios(
        current_user=current_user, 
        db_session=db_session
    )


@router.get(
    "/{estudio_id}",
    response_model=EstudioResponseSchema,
    summary="Busca um estúdio pelo ID."
)
def get_estudio_by_id_route(
    estudio_id: int,
    db_session: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return estudio_controller.get_estudio_by_id(
        estudio_id=estudio_id, 
        current_user=current_user, 
        db_session=db_session
    )


@router.patch(
    "/{estudio_id}",
    response_model=EstudioResponseSchema,
    summary="Atualiza dados de um estúdio. (Requer permissão de Admin)"
)
def update_estudio_route(
    estudio_id: int,
    update_data: EstudioUpdateSchema,
    db_session: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return estudio_controller.update_estudio(
        estudio_id=estudio_id, 
        update_data=update_data, 
        current_user=current_user, 
        db_session=db_session
    )


@router.delete("/{id_estudio}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir estudio por ID(Requer Autorização de Admin)"        
)
def delete_estudio_router(
    estudio_id: int,
    db: Session = Depends(get_db),
    current_user:dict=Depends(auth_manager)
):
    return estudio_controller.delete_estudio_controller(estudio_id=estudio_id,current_user=current_user, db_session=db)
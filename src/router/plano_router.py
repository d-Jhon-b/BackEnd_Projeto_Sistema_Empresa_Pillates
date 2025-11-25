from fastapi import APIRouter, status, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.controllers.plano_controller import PlanosController
from src.controllers.plano_personalizado_controller import PlanosPersonalizadosController
from src.controllers.planos_geral_controller import ConsultaPlanosGeralController

from src.schemas.plano_schemas import PlanoCreate, PlanoResponse, PlanoUpdate
from src.schemas.planos_personalizados_schemas import PlanoPersonalizadoCreate, PlanoPersonalizadoResponse, PlanoPersonalizadoUpdate

from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager 

router = APIRouter(
    prefix="/planos",
    tags=["Gestão de Planos (Padrão e Personalizado)"]
)

planos_controller = PlanosController()
planos_personalizados_controller = PlanosPersonalizadosController()
planos_geral_controller = ConsultaPlanosGeralController()



@router.get(
    "/geral",
    response_model=List[Dict[str, Any]], 
    summary="Lista todos os Planos (Padrão e Personalizados) combinados (Requer Autenticação padrão)"
)
def get_all_planos_geral_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_geral_controller.get_all_planos_geral(session_db=db, current_user=current_user)


# @router.get(
#     "/meu_plano",
#     response_model=PlanoResponse,
#     summary="Busca um Plano Padrão por ID (Requer Autenticação padrão)"
# )
# def get_plano_padrao_by_id_endpoint(
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(auth_manager)
# ):
#     return planos_controller.get_plano_padrao_by_id(
#         session_db=db, 
#         current_user=current_user
#     )

@router.post(
    "/padrao",
    response_model=PlanoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo Plano Padrão (Requer Autenticação de Admin)"
)
def create_plano_padrao_endpoint(
    data_plano: PlanoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_controller.create_plano_padrao(session_db=db, data_plano=data_plano, current_user=current_user)


@router.get(
    "/padrao",
    response_model=List[PlanoResponse],
    summary="Lista todos os Planos Padrão (Requer Autenticação padrão)"
)
def get_all_planos_padrao_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_controller.get_all_planos_padrao(session_db=db, current_user=current_user)

@router.get(
    "/padrao/{plano_id}",
    response_model=PlanoResponse,
    summary="Busca um Plano Padrão por ID (Requer Autenticação padrão)"
)
def get_plano_padrao_by_id_endpoint(
    plano_id: int = Path(..., description="ID do Plano Padrão"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_controller.get_plano_padrao_by_id(
        plano_id=plano_id, 
        session_db=db, 
        current_user=current_user
    )


@router.patch(
    "/padrao/{plano_id}",
    response_model=PlanoResponse,
    summary="Atualiza dados de um Plano Padrão por ID (Requer Autenticação de Admin)"
)
def update_plano_padrao_endpoint(
    plano_id: int = Path(..., description="ID do Plano Padrão a ser atualizado"),
    data_update: PlanoUpdate = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_controller.update_plano_padrao(
        plano_id=plano_id, 
        session_db=db, 
        data_update=data_update, 
        current_user=current_user
    )


@router.delete(
    "/padrao/{plano_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um Plano Padrão por ID (Requer Autenticação de Admin)"
)
def delete_plano_padrao_endpoint(
    plano_id: int = Path(..., description="ID do Plano Padrão a ser excluído"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    planos_controller.delete_plano_padrao(plano_id=plano_id, session_db=db, current_user=current_user)
    return None 


@router.post(
    "/personalizado",
    response_model=PlanoPersonalizadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo Plano Personalizado (Requer Autenticação de Admin)"
)
def create_plano_personalizado_endpoint(
    data_plano: PlanoPersonalizadoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_personalizados_controller.create_plano_personalizado(session_db=db, data_plano=data_plano, current_user=current_user)

@router.get(
    "/personalizado",
    response_model=List[PlanoPersonalizadoResponse],
    summary="Lista todos os Planos Personalizados (Requer Autenticação padrão)"
)
def get_all_planos_personalizados_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_personalizados_controller.get_all_planos_personalizados(session_db=db, current_user=current_user)


@router.get(
    "/personalizado/{plano_id}",
    response_model=PlanoPersonalizadoResponse,
    summary="Busca um Plano Personalizado por ID (Requer Autenticação padrão)"
)
def get_plano_personalizado_by_id_endpoint(
    plano_id: int = Path(..., description="ID do Plano Personalizado"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_personalizados_controller.get_plano_personalizado_by_id(plano_id=plano_id, session_db=db, current_user=current_user)


@router.patch(
    "/personalizado/{plano_id}",
    response_model=PlanoPersonalizadoResponse,
    summary="Atualiza dados de um Plano Personalizado por ID (Requer Autenticação de Admin)"
)
def update_plano_personalizado_endpoint(
    plano_id: int = Path(..., description="ID do Plano Personalizado a ser atualizado"),
    data_update: PlanoPersonalizadoUpdate = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return planos_personalizados_controller.update_plano_personalizado(
        plano_id=plano_id, 
        session_db=db, 
        data_update=data_update, 
        current_user=current_user
    )


@router.delete(
    "/personalizado/{plano_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um Plano Personalizado por ID (Requer Autenticação de Admin)"
)
def delete_plano_personalizado_endpoint(
    plano_id: int = Path(..., description="ID do Plano Personalizado a ser excluído"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    planos_personalizados_controller.delete_plano_personalizado(plano_id=plano_id, session_db=db, current_user=current_user)
    return None

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session

from typing import Any, Dict, List, Optional
from src.schemas.user_schemas import ColaboradorCreatePayload, UserResponse
# from src.controllers.userController import UserController

from src.controllers.colaboradores_controller import ColaboradoreController


from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import InstrutorCreatePayload, UserResponse
from src.schemas.user_schemas import AlunoCreatePayload, UserResponse



router = APIRouter(prefix="/colaboradore", tags=["Colaboradores"])
colaborador_controller = ColaboradoreController()

@router.post("/createColaborador", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_colaborador_endpoint(
    payload: ColaboradorCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return colaborador_controller.create_colaborador(payload, current_user, db_session=db)



@router.get("/{user_id}", response_model=UserResponse, 
            summary="Obter um colaborador por ID (Requer Autenticação de Admin ou o próprio colaborador)")
def select_colaborador_by_id_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return colaborador_controller.select_colaborador_by_id_controller(user_id=user_id, current_user=current_user, db_session=db)




@router.get("/", response_model=List[UserResponse], 
            summary="Listar todos os colaboradores por estúdio (Requer Autenticação de Admin)")
def select_all_colaboradores_endpoint(
    studio_id: Optional[int] = Query(None, 
    description="""
    - ID do estúdio para filtrar os colaboradores. 
    - Se omitido, o sistema usará o ID do estúdio do usuário logado.
    """
    ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return colaborador_controller.select_all_colaboradores_controller(studio_id=studio_id, current_user=current_user, db_session=db)

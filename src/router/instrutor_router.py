from fastapi import APIRouter, status, Depends, Query, Path
from sqlalchemy.orm import Session
from src.schemas.user_schemas import InstrutorCreatePayload, UserResponse, InstrutorUpdatePayload
# from src.controllers.userController import UserController
from src.controllers.instrutor_controller import InstrutorController
from typing import List, Optional

from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager

router = APIRouter(prefix="/instrutores", tags=["Instrutores"])

instrutor_controller = InstrutorController()

@router.post("/createInstrutor", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
description=""             
)
def create_instrutor_endpoint(
    payload: InstrutorCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return instrutor_controller.create_instrutor(payload, current_user, db_session=db)

@router.get("/{user_id}", response_model=UserResponse, summary="Listar instrutores por id(Requer autenticação de Admin)")
def get_instructor_by_id_endpoint(
    user_id:int,
    db:Session=Depends(get_db),
    current_user:dict=Depends(auth_manager)
):
    return instrutor_controller.select_instructor_by_id(user_id=user_id, current_user=current_user, db_session=db)

@router.get("/", response_model=List[UserResponse], summary="Listar todos os instrutores por estudio (Requer autenticação de Admin)")
def get_all_instructor_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager),
    studio_id: Optional[int] = Query(None,
    description="""
    - ID do estúdio para filtrar os colaboradores. 
    - Se omitido, o sistema usará o ID do estúdio do usuário logado.
    """
    ) 
):
    return instrutor_controller.select_all_instructor_controller(
        studio_id=studio_id,
        current_user=current_user,
        db_session=db
    )




@router.patch("/instrutores/{user_id}", 
    response_model=UserResponse, 
    status_code=status.HTTP_200_OK, 
    summary="Atualizar dados de um INSTRUTOR (Requer Próprio Acesso ou Admin)"
)
def update_instrutor_endpoint(
    update_data: InstrutorUpdatePayload, # Payload Focado
    user_id: int = Path(..., description="ID do Instrutor."),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    
    return instrutor_controller.update_instrutor_data(
        user_id=user_id,
        update_data=update_data,
        current_user=current_user,
        db_session=db
    )

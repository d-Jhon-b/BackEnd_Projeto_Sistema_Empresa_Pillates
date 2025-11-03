from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Importe os schemas, dependências e o controller
from src.schemas.user_schemas import UserResponse
from src.controllers.userController import UserController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager
from fastapi import HTTPException

router = APIRouter(
    prefix="/users",
    tags=["Users - Consultas"] 
)

user_controller = UserController()


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Listar todos os usuários por estudio(Requer Autenticação de admin)"
)
def get_all_users_endpoint(
    # studio_id: Optional[int] = None, 
    studio_id: Optional[int] = Query(None, 
    description="""
    -ID do estúdio para filtrar os usuários.(obrigatorio)
    """
    ), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return user_controller.get_all_users(studio_id, current_user, db_session=db)

@router.get("/me", response_model=UserResponse, summary="Selecionar minhas informações(Requer Autenticação padrão)")
def get_current_user_me(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    my_user_id = current_user.get("id_user")
    if my_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, não foi possível identificar o usuário."
        )

    return user_controller.get_user_by_id(
        user_id=my_user_id,
        current_user=current_user,
        db_session=db
    )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obter um usuário por ID (Requer Autenticação de admin)"
)
def get_user_by_id_endpoint(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    # my_user_id = current_user.get("fk_id_estudio")
    return user_controller.get_user_by_id(user_id, current_user, db_session=db)


@router.delete("/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Excluir um usuário por ID (Requer Autenticação de Admin)"
)
def delete_user_by_id_endpoint(
    user_id:int,
    db:Session =Depends(get_db),
    current_user:dict=Depends(auth_manager)
):
    return user_controller.delete_user_by_id_controller(current_user, user_id, db_session=db)




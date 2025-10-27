from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.orm import Session
from src.schemas.user_schemas import InstrutorCreatePayload, UserResponse
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
    studio_id: Optional[int] = None 
):
    return instrutor_controller.select_all_instructor_controller(
        studio_id=studio_id,
        current_user=current_user,
        db_session=db
    )
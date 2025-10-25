from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.schemas.user_schemas import ColaboradorCreatePayload, UserResponse
from src.controllers.userController import UserController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import InstrutorCreatePayload, UserResponse
from src.schemas.user_schemas import AlunoCreatePayload, UserResponse



router = APIRouter(prefix="/colaboradore", tags=["Colaboradores"])
user_controller = UserController()

@router.post("/createColaborador", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_colaborador_endpoint(
    payload: ColaboradorCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return user_controller.create_colaborador(payload, current_user, db_session=db)

@router.post("/createInstrutor", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_instrutor_endpoint(
    payload: InstrutorCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return user_controller.create_instrutor(payload, current_user, db_session=db)

@router.post("/createAluno", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_aluno_endpoint(
    payload: AlunoCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return user_controller.create_aluno(payload, current_user, db_session=db)
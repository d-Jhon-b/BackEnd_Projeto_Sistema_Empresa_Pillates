from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.schemas.user_schemas import AlunoCreatePayload, UserResponse
from src.controllers.userController import UserController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager

router = APIRouter(prefix="/alunos", tags=["Alunos"])
user_controller = UserController()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_aluno_endpoint(
    payload: AlunoCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return user_controller.create_aluno(payload, current_user, db_session=db)
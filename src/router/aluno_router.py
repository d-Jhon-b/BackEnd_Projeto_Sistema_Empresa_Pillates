from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.schemas.user_schemas import AlunoCreatePayload, UserResponse
# from src.controllers.userController import UserController
from fastapi import HTTPException

from typing import List, Optional

from src.controllers.aluno_controller import AlunoController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager

router = APIRouter(prefix="/alunos", tags=["Alunos"])
aluno_controller = AlunoController()


# @router.get("/me", response_model=UserResponse)
# def get_current_aluno_me(
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(auth_manager)
# ):
#     my_user_id = current_user.get("id_user")
#     if my_user_id is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token inválido, não foi possível identificar o usuário."
#         )

#     return aluno_controller.select_user_by_id(
#         user_id=my_user_id,
#         current_user=current_user,
#         db_session=db
#     )


@router.post("/createAluno", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
summary="Criar novo aluno (Requer autenticação de Admin)"             
)
def create_aluno_endpoint(
    payload: AlunoCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aluno_controller.create_aluno(payload, current_user, db_session=db)


@router.get("/{user_id}", response_model=UserResponse, summary="Listar alunos por id(Requer autenticação de Admin)")
def get_aluno_by_id_endpoint(
    user_id:int,
    db:Session=Depends(get_db),
    current_user:dict=Depends(auth_manager)
):
    return aluno_controller.select_user_by_id(user_id=user_id, current_user=current_user, db_session=db)

@router.get("/", response_model=List[UserResponse], summary="Listar todos os alunos por estudio (Requer autenticação de Admin)")
def get_all_alunos_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager),
    studio_id: Optional[int] = None # Parâmetro de query opcional
):
    return aluno_controller.select_all_aluno_controller(
        studio_id=studio_id,
        current_user=current_user,
        db_session=db
    )
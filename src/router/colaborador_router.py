from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
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



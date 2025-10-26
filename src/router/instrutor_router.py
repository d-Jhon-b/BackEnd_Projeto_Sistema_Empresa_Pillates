from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.schemas.user_schemas import InstrutorCreatePayload, UserResponse
# from src.controllers.userController import UserController
from src.controllers.instrutor_controller import InstrutorController


from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager

router = APIRouter(prefix="/instrutores", tags=["Instrutores"])
instrutor_controller = InstrutorController()

@router.post("/createInstrutor", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_instrutor_endpoint(
    payload: InstrutorCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return instrutor_controller.create_instrutor(payload, current_user, db_session=db)

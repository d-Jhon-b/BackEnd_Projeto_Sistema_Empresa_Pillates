from fastapi import APIRouter, status
from src.schemas.user_schemas import UserCreatePayload, UserResponse
from src.controllers.userController import UserController

router = APIRouter(
    prefix="/users",
    tags=["Users"] # Agrupa os endpoints na documentação do Swagger UI
)

user_controller = UserController()

@router.post(
    "/", 
    response_model=UserResponse, # Define o formato da resposta de sucesso
    status_code=status.HTTP_201_CREATED # Retorna 201 Created em vez de 200 OK
)
def create_user_endpoint(payload: UserCreatePayload):
    return user_controller.create_user(payload)
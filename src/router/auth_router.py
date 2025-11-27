from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.schemas.user_schemas import LoginRequestSchema, TokenResponseSchema, ForgotPasswordSchema, ResetPasswordSchema
# from src.controllers.userController import UserController
from src.database.dependencies import get_db

from src.services.authService import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# user_controller = UserController()

@router.post(
    "/login",
    response_model=TokenResponseSchema,
    summary="Obter um Token de Acesso"
)
def login_endpoint(
    payload: LoginRequestSchema,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db_session=db)
    # return auth_service.login_for_access_token(payload, db_session=db)
    return auth_service.login_for_access_token(payload)


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Solicitar redefinição de senha"
)
async def forgot_password_endpoint(
    payload: ForgotPasswordSchema,
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db_session=db)
    return await auth_service.forgot_password(payload, background_tasks)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Redefinir a senha com um token válido"
)
def reset_password_endpoint(
    payload: ResetPasswordSchema,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db_session=db)
    return auth_service.reset_password(payload)
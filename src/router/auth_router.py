# src/router/auth_router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.schemas.user_schemas import LoginRequestSchema, TokenResponseSchema
from src.controllers.userController import UserController
from src.database.dependencies import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

user_controller = UserController()

@router.post(
    "/login",
    response_model=TokenResponseSchema,
    summary="Obter um Token de Acesso"
)
def login_endpoint(
    payload: LoginRequestSchema,
    db: Session = Depends(get_db)
):
    """Authenticates the user and returns a JWT."""
    return user_controller.login_for_access_token(payload, db_session=db)
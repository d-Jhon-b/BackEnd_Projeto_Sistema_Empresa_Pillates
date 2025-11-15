from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connPostGreNeon import CreateSessionPostGre
from src.controllers.planoController import (
    criar_plano_controller,
    listar_planos_controller,
    meus_planos_controller
)
from src.controllers.validations.permissionValidation import UserValidation
from src.schemas.plano_schemas import PlanoCreate, PlanoDetalhe
from src.schemas.user_schemas import UserResponse

router = APIRouter(
    prefix="/planos",
    tags=["Planos"]
)

def get_db():
    create = CreateSessionPostGre()
    db = create.get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PlanoDetalhe, status_code=status.HTTP_201_CREATED)
def cadastrar_plano(
    plano: PlanoCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends()   # ← sem nenhum arquivo extra
):
    UserValidation.check_permission(current_user, ["SUPREMO", "ADMIN"])

    novo_plano = criar_plano_controller(
        usuario_id=current_user.get("id_user"),
        plano_dados=plano.dict(),
        session=db
    )
    return novo_plano


@router.get("/", response_model=list[PlanoDetalhe])
def listar_planos(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends()
):
    UserValidation.check_permission(current_user, ["SUPREMO"])

    planos = listar_planos_controller(
        usuario_id=current_user.get("id_user"),
        session=db
    )
    return planos


@router.get("/meus", response_model=list[PlanoDetalhe])
def meus_planos(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends()
):
    planos = meus_planos_controller(
        usuario_id=current_user.get("id_user"),
        session=db
    )
    return planos


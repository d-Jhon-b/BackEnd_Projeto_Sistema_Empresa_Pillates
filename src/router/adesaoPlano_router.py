from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.controllers.adesãoPlanoController import (
    criar_adesao_controller,
    listar_adesoes_usuario_controller
)
from src.controllers.validations.permissionValidation import UserValidation
from src.database.connPostGreNeon import CreateSessionPostGre


router = APIRouter(prefix="/adesao", tags=["Adesao"])


def get_db():
    create = CreateSessionPostGre()
    db = create.get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def criar_adesao(plano_id: int, data_validade: str, db: Session = Depends(get_db), current_user=Depends()):
    UserValidation.check_permission(current_user, ["ADMIN", "SUPREMO"])

    return criar_adesao_controller(
        usuario_id=current_user.get("id_user"),
        plano_id=plano_id,
        data_validade=data_validade,
        session=db
    )


@router.get("/me")
def minhas_adesoes(db: Session = Depends(get_db), current_user=Depends()):
    return listar_adesoes_usuario_controller(
        usuario_id=current_user.get("id_user"),
        session=db
    )


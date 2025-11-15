from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.controllers.atribuiçõesController import (
    atribuir_contrato_controller,
    atribuir_plano_controller,
    atribuir_adesao_plano_controller
)
from src.controllers.validations.permissionValidation import UserValidation
from src.database.connPostGreNeon import CreateSessionPostGre

router = APIRouter(prefix="/atribuir", tags=["Atribuições"])


def get_db():
    create = CreateSessionPostGre()
    db = create.get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/contrato")
def atribuir_contrato(db: Session = Depends(get_db), current_user=Depends()):
    UserValidation.check_permission(current_user, ["ADMIN", "SUPREMO"])
    return atribuir_contrato_controller(current_user.get("id_user"), db)


@router.post("/plano")
def atribuir_plano(plano_id: int, db: Session = Depends(get_db), current_user=Depends()):
    UserValidation.check_permission(current_user, ["ADMIN", "SUPREMO"])
    return atribuir_plano_controller(current_user.get("id_user"), plano_id, db)


@router.post("/adesao-plano")
def atribuir_adesao_plano(plano_id: int, data_validade: str, db: Session = Depends(get_db), current_user=Depends()):
    UserValidation.check_permission(current_user, ["ADMIN", "SUPREMO"])
    return atribuir_adesao_plano_controller(
        current_user.get("id_user"),
        plano_id,
        data_validade,
        db
    )

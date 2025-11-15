from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.controllers.contratoController import criar_contrato_controller, listar_contratos_usuario_controller
from src.database.connPostGreNeon import CreateSessionPostGre
from src.controllers.validations.permissionValidation import UserValidation

router = APIRouter(prefix="/contratos", tags=["Contratos"])


def get_db():
    create = CreateSessionPostGre()
    db = create.get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def criar_contrato(dados: dict, db: Session = Depends(get_db), current_user=Depends()):
    UserValidation.check_permission(current_user, ["ADMIN", "SUPREMO"])
    dados["fk_id_user"] = current_user.get("id_user")
    return criar_contrato_controller(dados, db)


@router.get("/me")
def meus_contratos(db: Session = Depends(get_db), current_user=Depends()):
    return listar_contratos_usuario_controller(
        user_id=current_user.get("id_user"),
        session=db
    )


from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager 
from src.controllers.adesao_plano_controller import AdesaoPlanoController
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, SubscribePlano

router = APIRouter(
    prefix="/adesao",
    tags=["Adesão de Planos"]
)

adesao_controller = AdesaoPlanoController()

@router.post(
    "/subscribe",
    response_model=SubscribePlano,
    status_code=status.HTTP_201_CREATED,
    summary="Realiza a adesão de um Plano (Requer Aluno ou Admin)"
)
def subscribe_plano_endpoint(
    data_payload: SubscribePlanoPayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    """
    Registra uma nova adesão de plano para um estudante.
    A validade é calculada automaticamente com base no tipo de plano.
    """
    return adesao_controller.subscribe_plano(
        session_db=db, 
        data_payload=data_payload, 
        current_user=current_user
    )
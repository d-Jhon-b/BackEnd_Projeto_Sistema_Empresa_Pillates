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



@router.get(
    "/estudante/{estudante_id}/pendente",
    response_model=SubscribePlano,
    summary="Busca a Adesão de Plano que está pendente de contratação (Requer Aluno ou Admin)"
)
def get_adesao_pendente_endpoint(
    estudante_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return adesao_controller.get_adesao_pendente_by_estudante(
        session_db=db, 
        estudante_id=estudante_id, 
        current_user=current_user
    )


@router.get(
    "/estudante/{estudante_id}/historico",
    response_model=list[SubscribePlano], # Retorna uma lista
    summary="Busca todas as Adesões de Plano (pendentes ou contratadas) para o estudante (Requer Aluno ou Admin)"
)
def get_historico_adesoes_endpoint(
    estudante_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    """
    Retorna o histórico completo de adesões de planos feitas pelo estudante.
    """
    return adesao_controller.get_all_adesoes_by_estudante(
        session_db=db, 
        estudante_id=estudante_id, 
        current_user=current_user
    )
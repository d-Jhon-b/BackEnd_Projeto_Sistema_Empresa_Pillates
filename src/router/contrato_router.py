from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager 
from src.controllers.contrato_controller import ContratoController
from src.schemas.contrato_schemas import ContratoCreate, ContratoResponse

router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"]
)

contrato_controller = ContratoController()

@router.post(
    "/create",
    response_model=ContratoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo Contrato formal a partir de uma Adesão de Plano (Requer Admin)"
)
def create_contrato_endpoint(
    data_payload: ContratoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    """
    Formaliza o Contrato de um aluno. Deve ser chamado após a Adesão do Plano.
    Requer permissão de Administrador.
    """
    return contrato_controller.create_contrato(
        session_db=db, 
        data_payload=data_payload, 
        current_user=current_user
    )

@router.get(
    "/{contrato_id}",
    response_model=ContratoResponse,
    summary="Busca um contrato pelo ID (Requer Admin)"
)
def get_contrato_endpoint(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    """
    Retorna os detalhes de um Contrato específico, incluindo planos associados.
    Requer permissão de Administrador (ajuste a validação se necessário).
    """
    return contrato_controller.select_contrato(
        session_db=db, 
        contrato_id=contrato_id, 
        current_user=current_user
    )
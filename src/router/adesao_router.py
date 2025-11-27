from fastapi import APIRouter, status, Depends,HTTPException
from sqlalchemy.orm import Session
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager 
from src.services.AdesaoContratoService import AdesaoContratoService
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, AdesaoPlanoBase,AdesaoPlanoUpdate
from src.controllers.validations.permissionValidation import UserValidation
from src.schemas.contrato_schemas import ContratoCreate,ContratoResponse,ContratoUpdate
from src.schemas.plano_detalhado_schemas import PlanoAtivoDetalhadoResponse
from src.controllers.contrato_controller import ContratoController

router = APIRouter(
    prefix="/planos",
    tags=["Planos - Adesão e Contrato"] 
)

def get_adesao_contrato_service(db: Session = Depends(get_db)) -> AdesaoContratoService:
    return AdesaoContratoService(db_session=db)
def get_plano_ativo_controller() -> ContratoController:
    return ContratoController()

@router.post(
    "/adesao",
    status_code=status.HTTP_201_CREATED,
    response_model=AdesaoPlanoBase, 
    summary="Aderir a um plano e gerar o contrato correspondente de forma atômica."
)
async def aderir_plano_e_gerar_contrato_endpoint(
    adesao_data: SubscribePlanoPayload,
    service: AdesaoContratoService = Depends(get_adesao_contrato_service),
    current_user: dict = Depends(auth_manager)
):
    UserValidation._check_admin_permission(current_user)
    estudante_id = adesao_data.fk_id_estudante
    result = service.create_adesao_and_contract(data=adesao_data, estudante_id=estudante_id, current_user=current_user)
    
    return result["adesao"]

@router.get(
    "/my-active-plano", 
    response_model=PlanoAtivoDetalhadoResponse, 
    summary="Busca o Contrato ativo/vigente do estudante logado (Meu Plano). (Requer Aluno/Admin)"
)
def get_my_active_plano_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager),
    controller: ContratoController = Depends(get_plano_ativo_controller)
):
    """
    Automaticamente encontra o ID do estudante logado (current_user) e retorna os 
    detalhes do Contrato ativo, que corresponde ao 'Meu Plano' do frontend.
    """
    # A validação de permissão de ALUNO está embutida no TargetUserFinder
    return controller.get_my_active_plano_and_contract(
        session_db=db, 
        current_user=current_user
    )


@router.delete(
    "/{adesao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui Adesão, Contrato e Pagamentos relacionados de forma atômica (Requer Admin)"
)
def delete_adesao_contrato_unificado(
    adesao_id: int,
    service: AdesaoContratoService = Depends(get_adesao_contrato_service),
    current_user: dict = Depends(auth_manager)
):
    
    success = service.delete_adesao_and_contract(adesao_id, current_user)
    
    if not success:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Adesão com ID {adesao_id} ou Contrato associado não encontrado para exclusão.")
    
    return 


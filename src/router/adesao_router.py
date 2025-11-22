from fastapi import APIRouter, status, Depends,HTTPException
from sqlalchemy.orm import Session
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager 
from src.services.AdesaoContratoService import AdesaoContratoService
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, AdesaoPlanoBase,AdesaoPlanoUpdate
from src.controllers.validations.permissionValidation import UserValidation

router = APIRouter(
    prefix="/planos",
    tags=["Planos - Adesão e Contrato"] 
)

def get_adesao_contrato_service(db: Session = Depends(get_db)) -> AdesaoContratoService:
    return AdesaoContratoService(db_session=db)


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


# @router.patch(
#     "/adesao/{adesao_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=AdesaoPlanoBase, # Use AdesaoPlanoBase ou um Response com o Contrato
#     summary="Atualiza campos não críticos de uma Adesão (e Contrato)."
# )
# async def atualizar_adesao_endpoint(
#     adesao_id: int,
#     data_update: AdesaoPlanoUpdate,
#     service: AdesaoContratoService = Depends(get_adesao_contrato_service),
#     current_user: dict = Depends(auth_manager)
# ):
#     UserValidation._check_admin_permission(current_user)

#     result = service.update_adesao_and_contract(adesao_id, data_update)

#     return result["adesao"]
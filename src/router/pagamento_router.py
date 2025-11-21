from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database.dependencies import get_db
from src.services.pagamentosService import PagamentoService 
from src.controllers.pagamento_controller import PagamentoController
from src.schemas.pagamento_schemas import PagamentoBase, PagamentoResponse, PagamentoInput
from src.services.authService import auth_manager
from src.controllers.validations.permissionValidation import UserValidation
from src.model.financasModel.pagamentoConfig import Pagamento


router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)

pagamento_controller = PagamentoController()


@router.get(f'/', status_code=status.HTTP_200_OK)
def get_all_pagamento_by_id_estudante_endpoint(
    id_estudante: int,
    current_user:dict=Depends(auth_manager),
    session: Session=Depends(get_db)
):

    return pagamento_controller.select_payment_by_estudante_controller(
        id_estudante=id_estudante,
        curent_user=current_user,
        session_db=session
    )

@router.get("/contrato/{id_contrato}", status_code=status.HTTP_200_OK)
def get_pagamentos_by_contrato_endpoint(
    id_contrato: int,
    current_user: dict = Depends(auth_manager),
    session: Session = Depends(get_db)
):
    return pagamento_controller.select_payments_by_contrato_controller(
        id_contrato=id_contrato,
        current_user=current_user,
        session_db=session
    )

def get_pagamento_service(session_db: Session = Depends(get_db)) -> PagamentoService:
    return PagamentoService(session_db=session_db)

@router.get("/{pagamento_id}", status_code=status.HTTP_200_OK)
def get_pagamento(
    pagamento_id: int, 
    service: PagamentoService = Depends(get_pagamento_service),
    current_user: dict = Depends(auth_manager),
    db: Session = Depends(get_db)
):  
    pagamento:Pagamento = service.get_pagamento_by_id(pagamento_id=pagamento_id, current_user=current_user)
    # target_user_id = pagamento.fk_id_estudante

    # UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
    return pagamento



@router.put("/{pagamento_id}/pay", status_code=status.HTTP_200_OK)
def pay_pagamento(
    pagamento_id: int, 
    pagamento_data: PagamentoInput,
    current_user: dict = Depends(auth_manager),
    service: PagamentoService = Depends(get_pagamento_service),
    db: Session = Depends(get_db)
):
    # if pagamento_data.metodo not in ['cartao', 'pix', 'dinheiro']:
    #      raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, 
    #         detail="Método de pagamento inválido."
    #     )
        
    updated_pagamento = service.registrar_pagamento(
            pagamento_id=pagamento_id, 
            metodo=pagamento_data.metodo.value, 
            current_user=current_user,
        )    
    return {"message": "Pagamento registrado com sucesso", "pagamento": updated_pagamento}
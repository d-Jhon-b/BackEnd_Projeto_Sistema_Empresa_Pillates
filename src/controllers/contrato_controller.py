from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.model.ContratoModel import ContratoModel
from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.schemas.contrato_schemas import ContratoCreate, ContratoResponse
from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.validations.ContratoValidations import ContratoValidation 
from src.model.UserModel import UserModel

class ContratoController:

    def create_contrato(self, session_db: Session, data_payload: ContratoCreate, current_user: Dict[str, Any]) -> ContratoResponse:
        
        UserValidation._check_admin_permission(current_user=current_user)
        
        contrato_repo = ContratoModel(session_db=session_db) 
        adesao_repo = AdesaoPlanoModel(session_db=session_db)
        fk_id_adesao = data_payload.fk_id_adesao_plano
        
        adesao_check = adesao_repo.select_adesao_by_id(fk_id_adesao)
        if not adesao_check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Adesão de Plano ID {fk_id_adesao} não encontrada.")
        ContratoValidation._check_adesao_contract_status(session_db=session_db, adesao_id=fk_id_adesao)
        # if adesao_repo.check_adesao_has_contrato(fk_id_adesao):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"A Adesão ID {fk_id_adesao} já possui um contrato formalizado."
        #     )
        
        dados_para_model = data_payload.model_dump(exclude_none=True) 

        try:
            # new_contrato = contrato_repo.insert_new_contrato(dados_para_model, current_user)
            result = contrato_repo.insert_new_contrato(dados_para_model, current_user)
            
            if result is None:
                raise Exception("Falha na persistência no banco de dados durante a criação do Contrato.")

            contrato_id, parcelas_db = result
            new_contrato = contrato_repo.select_contrato_by_id(contrato_id) 

            if new_contrato is None:
                raise Exception("Contrato criado, mas falha ao recuperá-lo do banco de dados.")
            return ContratoResponse.model_validate(new_contrato)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro no serviço de criação de Contrato: {e}"
            )
        
    def select_contrato(self, session_db: Session, contrato_id: int, current_user: Dict[str, Any]) -> ContratoResponse:
        contrato_repo = ContratoModel(session_db=session_db) 
        contrato_db = contrato_repo.select_contrato_by_id(contrato_id)
        target_user_id = contrato_db.fk_id_estudante
        
        # print(f'{target_user_id}\n\n\n\n\n')
        UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        
        if not contrato_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Contrato com ID {contrato_id} não encontrado."
            )
        
        # Serializa para o DTO
        return ContratoResponse.model_validate(contrato_db)
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from src.model.ContratoModel import ContratoModel
from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.schemas.contrato_schemas import ContratoCreate, ContratoResponse, ContratoUpdate
from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.validations.ContratoValidations import ContratoValidation 
from src.model.UserModel import UserModel
from src.model.AlunoModel import AlunoModel
from src.model.userModel.typeUser.aluno import Estudante
from src.controllers.utils.TargetUserFinder import TargetUserFinder


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

        contrato_ativo_existente = contrato_repo.select_active_contract_by_estudante(adesao_check.fk_id_estudante)
    
        if contrato_ativo_existente:
            if contrato_ativo_existente.status_contrato in ['ativo', 'suspenso']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"O estudante já possui um contrato '{contrato_ativo_existente.status_contrato}'. Crie um novo contrato apenas após o término ou cancelamento do contrato existente (ID: {contrato_ativo_existente.id_contrato})."
                )
        dados_para_model = data_payload.model_dump(exclude_none=True) 

        try:
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

        if not contrato_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Contrato com ID não encontrado."
                # detail=f"Contrato com ID {contrato_id} não encontrado."
            )
        # estudante_model = AlunoModel(db_session=session_db)
        # id_user = estudante_model.select_id_user_by_fk_id_estudante(contrato_db.fk_id_estudante)
        # target_user_id = id_user
        # if not target_user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        #         detail="Contrato encontrado, mas estudante associado não localizado."
        #     )
        
        # UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        # if not contrato_db:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, 
        #         detail=f"Contrato com ID {contrato_id} não encontrado."
        #     )
        
        TargetUserFinder.check_and_get_target_user_id(session_db, contrato_db.fk_id_estudante, current_user)
        return ContratoResponse.model_validate(contrato_db)
    


    def select_active_contrato_by_estudante(self, session_db: Session, estudante_id: int, current_user: Dict[str, Any]) -> Optional[ContratoResponse]:

        # estudante_model = AlunoModel(db_session=session_db)
        # target_user_id = estudante_model.select_id_user_by_fk_id_estudante(estudante_id)
        
        # if not target_user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, 
        #         detail=f"Estudante ID {estudante_id} não encontrado ou sem usuário associado."
        #     )
            
        # UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        TargetUserFinder.check_and_get_target_user_id(session_db, estudante_id, current_user)
        contrato_repo = ContratoModel(session_db=session_db)
        contrato_db = contrato_repo.select_active_contract_by_estudante(estudante_id)
        
        # if not contrato_db:
        #     return None 
        if contrato_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Nenhum contrato ativo ou suspenso encontrado para o estudante ID {estudante_id}."
            )
        return ContratoResponse.model_validate(contrato_db)
    

    def select_all_contratos_by_estudante(self, session_db: Session, estudante_id: int, current_user: Dict[str, Any]) -> List[ContratoResponse]:
        # estudante_model = AlunoModel(db_session=session_db)
        # target_user_id = estudante_model.select_id_user_by_fk_id_estudante(estudante_id)
        
        # if not target_user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, 
        #         detail=f"Estudante ID {estudante_id} não encontrado ou sem usuário associado."
        #     )
            
        # UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        TargetUserFinder.check_and_get_target_user_id(session_db, estudante_id, current_user)
        contrato_repo = ContratoModel(session_db=session_db)
        contratos_db = contrato_repo.select_all_contracts_by_estudante(estudante_id)
        
        if not contratos_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Nenhum histórico de contrato encontrado para o estudante ID {estudante_id}."
            )
        
        return [ContratoResponse.model_validate(c) for c in contratos_db]
    


    def update_contrato(self, session_db: Session, contrato_id: int, data_payload: ContratoUpdate, current_user: Dict[str, Any]) -> ContratoResponse:    
        UserValidation._check_admin_permission(current_user=current_user)
        
        contrato_repo = ContratoModel(session_db=session_db)
        
        contrato_db = contrato_repo.select_contrato_by_id(contrato_id)
        if not contrato_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Contrato com ID {contrato_id} não encontrado."
            )

        data_to_update = data_payload.model_dump(exclude_none=True)
        
        if not data_to_update:
            return ContratoResponse.model_validate(contrato_db) # Nada para atualizar

        try:
            updated_contrato = contrato_repo.update_contrato(contrato_id, data_to_update)
            
            if updated_contrato is None:
                raise Exception(f"Falha na atualização do Contrato ID {contrato_id}.")
                
            return ContratoResponse.model_validate(updated_contrato)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro no serviço de atualização de Contrato: {e}"
            )
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.model.SolicitacoesModel import SolicitacoesModel
from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import (UserResponse, 
LoginRequestSchema, 
NivelAcessoEnum, 
AlunoCreatePayload, 
InstrutorCreatePayload, 
ColaboradorCreatePayload,
)
from src.controllers.validations.permissionValidation import UserValidation
from src.schemas.solicitacao_schemas import SolicitacaoCreate, SolicitacaoUpdate, SolicitacaoResponseSchema
from src.controllers.validations.statusSolicitacaoValidation import ValidarStatus

class SolicitacaoController():
    def create_new_request(self, session_db:Session, data_request:SolicitacaoCreate, current_user: Dict[str, Any]):
        UserValidation._check_all_permission(current_user)
        try:

            user_id = current_user.get("id_user")
            fk_id_estudio = current_user.get("fk_id_estudio")

            if user_id is None or fk_id_estudio is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Dados do usuário inválidos."
                )

            solicitacao_data = SolicitacaoCreate(
                fk_id_user=user_id,
                fk_id_estudio=fk_id_estudio,
                menssagem=data_request.menssagem,
                tipo_de_solicitacao=data_request.tipo_de_solicitacao
            )

            solicitacao_model = SolicitacoesModel(session_db=session_db)
            new_request = solicitacao_model.create_solicitacao(solicitacao_data)

            return SolicitacaoResponseSchema.model_validate(new_request)
        
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao criar solicitação: {err}"
            )

    def update_request_status(self,id_solicitacao:int, session_db:Session, data_request:SolicitacaoUpdate, current_user: Dict[str, Any]):
        UserValidation._check_admin_permission(current_user)
        if not data_request.model_dump(by_alias=True, exclude_none=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo fornecido para atualização."
            )

        try:
            self.type_request = 'update_request_status'
            ValidarStatus.validar_status(session_db=session_db, id_solcitacao=id_solicitacao)    
            solicitacao_model = SolicitacoesModel(session_db=session_db)
            self.updated_solicitacao = solicitacao_model.update_solicitacao(id_solcitacao=id_solicitacao, solicitacao_data=data_request)
            
            if not self.updated_solicitacao:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Solicitação com ID {id_solicitacao} não encontrado."
                )
            
            return SolicitacaoResponseSchema.model_validate(self.updated_solicitacao)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao processar solicitação: {err}"
            )
        
    def select_all_solicitacoes(self,session_db:Session,current_user:dict, id_estudio:int | None):
        UserValidation._check_admin_permission(current_user=current_user)
        fk_id_estudio = current_user.get('fk_id_estudio')
        try:
            solicitacoes_model=SolicitacoesModel(session_db=session_db)
            lv_acesso = current_user.get('lv_acesso')
            # if id_estudio is None:
            #     solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes(fk_id_estudio)
            if id_estudio is None:
                if lv_acesso == NivelAcessoEnum.SUPREMO.value:
                    solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes() #Vai buscar todas as solicitações de todos os estudios
                else:
                    solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes(fk_id_estudio)
            else:
                solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes(id_estudio)
            return [SolicitacaoResponseSchema.model_validate(solicitacoes) for solicitacoes in solicitacoes_from_db]
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao processar solicitação de busca das solicitações: {err}"
            )

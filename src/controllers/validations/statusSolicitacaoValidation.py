from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import select
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.schemas.solicitacao_schemas import StatusSolcitacaoEnum

class ValidarStatus:
    @staticmethod
    def validar_status(session_db:Session, id_solcitacao:int):
        try:
            stmt_select = select(Solicitacoes.status_solicitacao).where(Solicitacoes.id_solicitacao == id_solcitacao)
            res_select = session_db.execute(stmt_select).unique().scalar_one_or_none()
            """Validação principal para update, não deixar alterar dados de uma solicitção que já foi aplicada"""
            if res_select != StatusSolcitacaoEnum.EM_ESPERA.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você não pode alterar uma solicitação que já foi respondida."
                )
            return True
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao validar status da solicitação no banco de dados."
            )
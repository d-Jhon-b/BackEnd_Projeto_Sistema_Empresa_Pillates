from fastapi import APIRouter, Depends, status, HTTPException, Query,Path
from sqlalchemy.orm import Session
from typing import List, Optional


from src.controllers.solicitacao_controller import SolicitacaoController
from src.schemas.solicitacao_schemas import SolicitacaoCreatePayload,SolicitacaoCreate, SolicitacaoUpdate, SolicitacoesBase, SolicitacaoResponseSchema, StatusSolcitacaoEnum, TipoDeSolicitacaoEnum
from src.database.dependencies import get_db 
from src.utils.authUtils import auth_manager # Importe sua função de autenticação

router = APIRouter(
    prefix="/solicitacao",
    tags=["Solicitações do Estudio"]
)

solicitacao_controller = SolicitacaoController()


@router.get(
    "/",
    response_model=List[SolicitacaoResponseSchema],
    summary="Listar todas as solicitações do estudio ao qual o admnistrador está associado."
)
def get_all_solicitacoes_endpoint(
    studio_id: Optional[int] = Query(None, 
    description=
    """
        -ID do estúdio para filtrar os usuários.(obrigatorio)
    """
    ), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
    ):
    return solicitacao_controller.select_all_solicitacoes(session_db=db, current_user=current_user, id_estudio=studio_id)


@router.post(
    "/createSolcicitacao",
    response_model=SolicitacaoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar nova solicitação para Colaboradores"
)
def create_new_request_endpoint(
    payload: SolicitacaoCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return solicitacao_controller.create_new_request(session_db=db, data_request=payload, current_user=current_user)


@router.patch(
"/responseSolicitacao/{id_solicitacao}",
response_model=SolicitacaoResponseSchema,
status_code=status.HTTP_200_OK,
summary="Alterar estado de uma solicitação para: 'aceita' ou 'recusada'. "
)
def update_request_endpoint(
    payload: SolicitacaoUpdate,
    db: Session=Depends(get_db),
    current_user: dict=Depends(auth_manager),    
    id_solicitacao: int = Path(..., description="Id para aplicar alteração em solicitacao")
):
    return solicitacao_controller.update_request_status(id_solicitacao=id_solicitacao, session_db=db, data_request=payload, current_user=current_user)


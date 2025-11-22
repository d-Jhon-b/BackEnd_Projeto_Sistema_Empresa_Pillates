from fastapi import APIRouter, Depends, status, HTTPException, Query,Path
from sqlalchemy.orm import Session
from typing import List, Optional
from starlette.concurrency import run_in_threadpool

from src.controllers.solicitacao_controller import SolicitacaoController
from src.schemas.solicitacao_schemas import SolicitacaoCreatePayload,SolicitacaoCreate, SolicitacaoUpdate, SolicitacoesBase, SolicitacaoResponseSchema, StatusSolcitacaoEnum, TipoDeSolicitacaoEnum
from src.database.dependencies import get_db 
from src.utils.authUtils import auth_manager # Importe sua função de autenticação

from src.model.AgendaModel import AgendaAulaRepository 

router = APIRouter(
    prefix="/solicitacao",
    tags=["Solicitações do Estudio"]
)

solicitacao_controller = SolicitacaoController()



def get_agenda_repo(db: Session = Depends(get_db)) -> AgendaAulaRepository:
    return AgendaAulaRepository(AgendaAulaRepository)

# def get_solicitacao_controller(db: Session = Depends(get_db)) -> SolicitacaoController:
#     return SolicitacaoController()

@router.get(
    "/",
    response_model=List[SolicitacaoResponseSchema],
    summary="Listar todas as solicitações do estudio ao qual o admnistrador está associado."
)
async def get_all_solicitacoes_endpoint( 
    studio_id: Optional[int] = Query(None, 
    description=
    """
        -ID do estúdio para filtrar os usuários.
        - Se for `None`: Admins normais listam as solicitações do próprio estúdio. Admins Supremos listam todas as solicitações.
    """
    ), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
    ):
    # 🚨 CORREÇÃO: Usar await run_in_threadpool para chamar o método síncrono do Controller
    return await run_in_threadpool(
        solicitacao_controller.select_all_solicitacoes,
        session_db=db, 
        current_user=current_user, 
        id_estudio=studio_id
    )


@router.post(
    "/createSolcicitacao",
    response_model=SolicitacaoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar nova solicitação para Colaboradores"
)
async def create_new_request_endpoint( # 🚨 MUDAR para async def
    payload: SolicitacaoCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return await run_in_threadpool(
        solicitacao_controller.create_new_request,
        session_db=db, 
        data_request=payload, 
        current_user=current_user
    )
@router.put(
    "/{id_solicitacao}/resolucao",
    status_code=status.HTTP_200_OK,
    summary="Atende ou Recusa uma solicitação de Aula, Plano, Pagamento ou Outros."
)


async def resolver_solicitacao_endpoint(
    id_solicitacao: int,
    status_solicitacao: StatusSolcitacaoEnum, 
    # controller: SolicitacaoController = Depends(get_solicitacao_controller),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_repo),
    session_db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    # O controller agora lida com toda a lógica transacional
    try:
        updated_solicitacao = await solicitacao_controller.handle_request_resolution(
            id_solicitacao=id_solicitacao,
            session_db=session_db,
            current_user=current_user,
            status_solicitacao=status_solicitacao,
            agenda_repo=agenda_repo
        )
        return {"mensagem": f"Solicitação {id_solicitacao} resolvida como {status_solicitacao.value}.", "solicitacao": updated_solicitacao}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro inesperado ao resolver solicitação: {e}")

# @router.patch(
# "/responseSolicitacao/{id_solicitacao}",
# response_model=SolicitacaoResponseSchema,
# status_code=status.HTTP_200_OK,
# summary="Alterar estado de uma solicitação para: 'aceita' ou 'recusada'. "
# )
# async def update_request_endpoint( # 🚨 MUDAR para async def
#     payload: SolicitacaoUpdate,
#     db: Session=Depends(get_db),
#     current_user: dict=Depends(auth_manager),     
#     id_solicitacao: int = Path(..., description="Id para aplicar alteração em solicitacao")
# ):

#     from src.model.AgendaModel import AgendaAulaRepository # Exemplo
#     agenda_repo = AgendaAulaRepository(db)

#     return await solicitacao_controller.handle_request_resolution(
#         id_solicitacao=id_solicitacao,
#         session_db=db,
#         current_user=current_user,
#         status_solicitacao=payload.status_solicitacao,
#         agenda_repo=agenda_repo
#     )




# @router.get(
#     "/",
#     response_model=List[SolicitacaoResponseSchema],
#     summary="Listar todas as solicitações do estudio ao qual o admnistrador está associado."
# )
# def get_all_solicitacoes_endpoint(
#     studio_id: Optional[int] = Query(None, 
#     description=
#     """
#         -ID do estúdio para filtrar os usuários.(obrigatorio)
#         - Se for `None`: Admins normais listam as solicitações do próprio estúdio. Admins Supremos listam todas as solicitações.
#     """
#     ), 
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(auth_manager)
#     ):
#     return solicitacao_controller.select_all_solicitacoes(session_db=db, current_user=current_user, id_estudio=studio_id)


# @router.post(
#     "/createSolcicitacao",
#     response_model=SolicitacaoResponseSchema,
#     status_code=status.HTTP_201_CREATED,
#     summary="Enviar nova solicitação para Colaboradores"
# )
# def create_new_request_endpoint(
#     payload: SolicitacaoCreatePayload,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(auth_manager)
# ):
#     return solicitacao_controller.create_new_request(session_db=db, data_request=payload, current_user=current_user)


# @router.patch(
# "/responseSolicitacao/{id_solicitacao}",
# response_model=SolicitacaoResponseSchema,
# status_code=status.HTTP_200_OK,
# summary="Alterar estado de uma solicitação para: 'aceita' ou 'recusada'. "
# )
# def update_request_endpoint(
#     payload: SolicitacaoUpdate,
#     db: Session=Depends(get_db),
#     current_user: dict=Depends(auth_manager),    
#     id_solicitacao: int = Path(..., description="Id para aplicar alteração em solicitacao")
# ):
#     return solicitacao_controller.update_request_status(id_solicitacao=id_solicitacao, session_db=db, data_request=payload, current_user=current_user)

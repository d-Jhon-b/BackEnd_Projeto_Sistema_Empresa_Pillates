from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorCollection

from src.database.dependencies import get_db, get_agenda_aulas_dependency, get_agenda_aluno_dependency
from src.controllers.agenda_controller import AgendaController
from src.controllers.aula_controller import AulaController
from src.controllers.agenda_aluno_controller import AgendaAlunoController

from src.model.AgendaModel import AgendaAulaRepository
from src.repository.ContratoRepository import ContratoRepository 
from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse,AgendaAlunoUpdate
from datetime import date
from typing import List
from src.services.authService import auth_manager

router = APIRouter(prefix="/agenda", tags=["Agenda e Cronograma (MongoDB)"])
agenda_controller = AgendaController()
aula_controller = AulaController()


def get_agenda_aula_repository(
    collection: AsyncIOMotorCollection = Depends(get_agenda_aulas_dependency) 
) -> AgendaAulaRepository:
    return AgendaAulaRepository(collection=collection)


def get_agenda_aluno_repository(
    collection: AsyncIOMotorCollection = Depends(get_agenda_aluno_dependency) 
) -> AgendaAlunoRepository:
    """Retorna uma instância do Repositório de Agenda do Aluno (MongoDB)."""
    return AgendaAlunoRepository(collection=collection)


def get_contrato_repository(
    db: Session = Depends(get_db)
) -> ContratoRepository:
    """Retorna uma instância do ContratoRepository (SQL)."""
    return ContratoRepository(db_session=db)


def get_agenda_aluno_controller(
    agenda_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository), 
    db: Session = Depends(get_db),
    contrato_repo: ContratoRepository = Depends(get_contrato_repository) 
) -> AgendaAlunoController:
    """Retorna uma instância do AgendaAlunoController."""
    return AgendaAlunoController(agenda_repo=agenda_repo, db_session=db, contrato_repo=contrato_repo) 


@router.post(
    "/aluno/registro",
    response_model=AgendaAlunoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Instrutor/Colaborador] Criar novo Registro de Aula para Estudante"
)
async def create_agenda_aluno_registro_endpoint(
    data: AgendaAlunoCreate,
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller),
    current_user: dict = Depends(auth_manager)
):
    """
    Cria um registro individual de aula na agenda do aluno no MongoDB.
    
    Observação: Esta rota não executa débito de aulas; o débito ocorre APENAS na atualização
    do status para 'Presente' via rota PATCH.
    """
    # Adicionar checagem de permissão, se necessário
    if current_user.get("lv_acesso") not in ["instrutor", "colaborador", "supremo"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado para criar registros de aluno.")
        
    return await agenda_aluno_ctrl.create_registro(data=data)

@router.patch(
    "/aluno/registro/{registro_id}",
    response_model=AgendaAlunoResponse,
    status_code=status.HTTP_200_OK,
    summary="[Instrutor/Colaborador] Atualizar Status de Presença e Debitar Aula (Transacional)"
)
async def update_status_presenca_endpoint(
    registro_id: str,
    update_data: AgendaAlunoUpdate,
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller),
    current_user: dict = Depends(auth_manager)
):

    if current_user.get("lv_acesso") not in ["instrutor", "colaborador", "supremo"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas instrutores/colaboradores podem registrar presença.")
    
    return await agenda_aluno_ctrl.update_status_presenca(
        registro_id=registro_id,
        update_data=update_data
    )


@router.get("/cronograma", response_model=List[AgendaAulaResponseSchema], summary="Buscar Cronograma de Aulas por Período")
async def get_cronograma_endpoint(
    start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    current_user: dict = Depends(auth_manager) 
):
    return await agenda_controller.get_cronograma(
        start_date=start_date,
        end_date=end_date,
        agenda_repository=agenda_repo,
        current_user=current_user
    )



@router.get("/minhas_aulas", response_model=List[AgendaAulaResponseSchema], summary="[ALUNO] Buscar Minhas Aulas Agendadas por Período")
async def get_my_aulas_endpoint(
  start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
  end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    db_sql: Session = Depends(get_db),
  agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
  current_user: dict = Depends(auth_manager) # Usar o auth_manager real
):
    if current_user.get("lv_acesso") not in ["aluno", "instrutor", "colaborador", "supremo"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    return await agenda_controller.get_my_aulas_by_period(
        start_date=start_date,
        end_date=end_date,
            current_user=current_user,
            db_session_sql=db_sql,
        agenda_repository=agenda_repo
    )


# @router.post("/createCronograma", response_model=List[AgendaAulaResponseSchema], summary="Criar novo Cronograma de Aulas mensal")
# async def create_cronograma_endpoint( 
#     start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
#     end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
#     agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
#     current_user: dict = Depends(auth_manager) 
# ):
#     return await agenda_controller.create_new_cronograma(start_date=start_date,
#         end_date=end_date,
#         agenda_repository=agenda_repo)


# def mock_current_user(): # Placeholder para autenticação
#     return {"user_id": 1, "access_level": "supremo"} 

# @router.post("/aula", response_model=AgendaAulaResponseSchema, status_code=status.HTTP_201_CREATED, summary="Agendar Nova Aula")
# async def agendar_aula_endpoint(
#     aula_data: AgendaAulaCreateSchema,
#     db_sql: Session = Depends(get_db), 
#     agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), 
#     current_user: dict = Depends(mock_current_user) 
# ):
#     return await aula_controller.create_new_aula(
#         aula_data=aula_data,
#         db_session_sql=db_sql,
#         agenda_repository=agenda_repo
#     )
# @router.get("/cronograma", response_model=List[AgendaAulaResponseSchema], summary="Buscar Cronograma de Aulas por Período")
# async def get_cronograma_endpoint( 
# ):
#     return await agenda_controller.get_cronograma(
#     )


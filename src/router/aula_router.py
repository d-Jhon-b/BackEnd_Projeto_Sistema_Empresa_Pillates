from fastapi import APIRouter, status, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.schemas.aulas_schemas import AulaResponse, AulaCreate, AulaUpdate, MatriculaCreate,AulaRecorrenteCreate, MatriculaSeriesCreate
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse, AgendaAlunoUpdate,StatusPresencaEnum
from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository

from src.controllers.aula_controller import AulaController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager
from src.controllers.excecao_controller import ExcecaoController

from src.model.AgendaModel import AgendaAulaRepository 
from src.router.agenda_router import get_agenda_aula_repository, get_agenda_aluno_repository
from src.router.excecao_router import get_excecao_controller_dependency

from src.controllers.agenda_aluno_controller import AgendaAlunoController



router = APIRouter(
    prefix="/aulas",
    tags=["Aulas - CRUD"] 
)

aula_controller = AulaController()

@router.get(
    "/{aula_id}",
    response_model=AulaResponse,
    summary="Obter detalhes de uma aula por ID (Requer Autenticação)"
)
def get_aula_by_id_endpoint(
    aula_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aula_controller.get_aula_by_id(aula_id, current_user, db_session=db)

@router.get(
    "/",
    response_model=List[AulaResponse],
    summary="Listar todas as aulas do estúdio (Requer Autenticação)"
)
def get_all_aulas_endpoint(
    studio_id: Optional[int] = Query(None, description="Opcional: ID do estúdio. Ignorado se não for SUPREMO."), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aula_controller.get_all_aulas(studio_id, current_user, db_session=db)

@router.post(
  "/",
  status_code=status.HTTP_201_CREATED,
  response_model=AulaResponse,
  summary="Criar uma nova aula (SQL) e agendar no cronograma (MongoDB)"
)
async def create_aula_endpoint( 
  aula_data: AulaCreate, 
  db: Session = Depends(get_db),
  agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), 
  excecao_controller: ExcecaoController = Depends(get_excecao_controller_dependency),
  current_user: dict = Depends(auth_manager)
):
    return await aula_controller.create_new_aula(aula_data, current_user, db_session=db, agenda_repo=agenda_repo,excecao_repo=excecao_controller.excecao_repo)


@router.patch( 
    "/{aula_id}",
    response_model=AulaResponse,
    summary="Atualizar dados de uma aula parcialmente (SQL e MongoDB) - Requer permissão de Admin/Colaborador"
)
async def patch_aula_endpoint(
    aula_id: int,
    update_data: AulaUpdate, 
    db: Session = Depends(get_db),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), 
    current_user: dict = Depends(auth_manager)
):
    return await aula_controller.update_aula(aula_id, update_data, current_user, db_session=db, agenda_repo=agenda_repo)


@router.delete(
    "/{aula_id}",
    status_code=status.HTTP_200_OK, 
    summary="Excluir uma aula por ID (SQL e MongoDB) - Requer Autenticação de Admin"
)
async def delete_aula_by_id_endpoint( # Tornar a função async
    aula_id: int,
    db: Session = Depends(get_db),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), # Injetar o repo do Mongo
    current_user: dict = Depends(auth_manager)
):
    return await aula_controller.delete_aula_by_id_controller(aula_id, current_user, db_session=db, agenda_repo=agenda_repo)


@router.post(
    "/{aula_id}/matricular",
    status_code=status.HTTP_201_CREATED,
    summary="Matricular um estudante em uma aula (Requer permissão de Admin/Colaborador)"
)
async def enroll_student_endpoint(
    aula_id: int,
    matricula_data: MatriculaCreate,
    db: Session = Depends(get_db),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    current_user: dict = Depends(auth_manager)
):
    return await aula_controller.enroll_student_in_aula(aula_id, matricula_data, current_user, db_session=db, agenda_repo=agenda_repo)




@router.post(
    "/create/recorrente",
    status_code=status.HTTP_201_CREATED,
    summary="Cria um conjunto de Aulas Recorrentes em um período, excluindo exceções (Admin)."
)
async def create_aulas_recorrentes_endpoint(
    recorrencia_data: AulaRecorrenteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    excecao_controller: ExcecaoController = Depends(get_excecao_controller_dependency),
    agenda_aluno_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository) 
):
    return await aula_controller.create_aulas_recorrentes(
        recorrencia_data=recorrencia_data,
        current_user=current_user,
        db_session=db,
        agenda_repo=agenda_repo,
        excecao_repo=excecao_controller.excecao_repo, 
        agenda_aluno_repo=agenda_aluno_repo
    )
@router.post(
    "/matricular/series",
    status_code=status.HTTP_201_CREATED,
    summary="Matricular um estudante em todas as aulas futuras de uma série (por Título da Aula)"
)
async def enroll_student_series_endpoint(
    matricula_data: MatriculaSeriesCreate,
    db: Session = Depends(get_db),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    agenda_aluno_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository), 
    current_user: dict = Depends(auth_manager)
):
    agenda_aluno_ctrl = AgendaAlunoController(db_session=db, agenda_aluno_repo=agenda_aluno_repo,agenda_aulas_repo=agenda_repo)

    return await aula_controller.enroll_student_in_series(
        matricula_data=matricula_data,
        current_user=current_user,
        db_session=db, 
        agenda_repo=agenda_repo,
        agenda_aluno_ctrl=agenda_aluno_ctrl
    )









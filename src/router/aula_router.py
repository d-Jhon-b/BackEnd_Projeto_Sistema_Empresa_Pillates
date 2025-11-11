from fastapi import APIRouter, status, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.schemas.aulas_schemas import AulaResponse, AulaCreate, AulaUpdate, MatriculaCreate
from src.controllers.aula_controller import AulaController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager

from src.model.AgendaModel import AgendaAulaRepository 
from src.router.agenda_router import get_agenda_aula_repository 

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
    # studio_id é opcional no Query, mas o controller o preencherá automaticamente
    # com o fk_id_estudio do usuário, a menos que seja SUPREMO.
    studio_id: Optional[int] = Query(None, description="Opcional: ID do estúdio. Ignorado se não for SUPREMO."), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aula_controller.get_all_aulas(studio_id, current_user, db_session=db)

# --- POST (INSERT) ---
@router.post(
  "/",
  status_code=status.HTTP_201_CREATED,
  response_model=AulaResponse,
  summary="Criar uma nova aula (SQL) e agendar no cronograma (MongoDB)"
)
async def create_aula_endpoint( # Tornar assíncrono para operações MongoDB
  aula_data: AulaCreate, 
  db: Session = Depends(get_db),
    # Injeta o Repositório do MongoDB
  agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), 
  current_user: dict = Depends(auth_manager)
):
    return await aula_controller.create_new_aula(aula_data, current_user, db_session=db, agenda_repo=agenda_repo)




@router.patch( # MUDANÇA: Substituímos o @router.put por @router.patch
    "/{aula_id}",
    response_model=AulaResponse,
    summary="Atualizar dados de uma aula parcialmente (Requer permissão de Admin/Colaborador)"
)
def patch_aula_endpoint( # Renomeado para melhor clareza (opcional)
    aula_id: int,
    update_data: AulaUpdate, # Continua usando o schema com campos opcionais
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    # Chama o mesmo método no Controller
    return aula_controller.update_aula(aula_id, update_data, current_user, db_session=db)

@router.delete(
    "/{aula_id}",
    status_code=status.HTTP_200_OK, 
    summary="Excluir uma aula por ID (Requer Autenticação de Admin)"
)
def delete_aula_by_id_endpoint(
    aula_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aula_controller.delete_aula_by_id_controller(aula_id, current_user, db_session=db)

@router.post(
    "/{aula_id}/matricular",
    status_code=status.HTTP_201_CREATED,
    summary="Matricular um estudante em uma aula (Requer permissão de Admin/Colaborador)"
)
def enroll_student_endpoint(
    aula_id: int,
    matricula_data: MatriculaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aula_controller.enroll_student_in_aula(aula_id, matricula_data, current_user, db_session=db)
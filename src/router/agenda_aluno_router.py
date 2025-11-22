
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorCollection


from src.database.dependencies import get_agenda_aluno_dependency, get_agenda_aulas_dependency, get_db 
from src.services.authService import auth_manager 
from src.controllers.agenda_aluno_controller import AgendaAlunoController 
from src.controllers.aula_controller import AulaController
from src.controllers.agenda_controller import AgendaController

from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository,AgendaAlunoUpdate
from src.repository.ContratoRepository import ContratoRepository 
from src.schemas.agenda_aluno_schemas import AgendaAlunoResponse
from src.schemas.agenda_schemas import AgendaAulaResponseSchema, AgendaAulaCreateSchema
from src.model.AgendaModel import AgendaAulaRepository


router = APIRouter(
    prefix="/agenda",
    tags=["Agenda de Aulas (Aluno)"],
)

# agenda_aluno_controller = AgendaAlunoController(db_session=get_db, agenda_aluno_repo=get_agenda_aluno_dependency)
# agenda_controller = AgendaController()
# aula_controller = AulaController()


def get_agenda_aula_repository(
    collection: AsyncIOMotorCollection = Depends(get_agenda_aulas_dependency) 
) -> AgendaAulaRepository:
    return AgendaAulaRepository(collection=collection)


def get_agenda_aluno_repository(
    collection: AsyncIOMotorCollection = Depends(get_agenda_aluno_dependency) 
) -> AgendaAlunoRepository:
    """Retorna uma instância do Repositório de Agenda do Aluno (MongoDB)."""
    return AgendaAlunoRepository(collection=collection)

# def get_contrato_repository(
#     db: Session = Depends(get_db)
# ) -> ContratoRepository:
#     """Retorna uma instância do ContratoRepository (SQL)."""
#     return ContratoRepository(db_session=db)

def get_agenda_aluno_controller(
    db: Session = Depends(get_db),
    agenda_aluno_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository)
) -> AgendaAlunoController:

    return AgendaAlunoController(db_session=db, agenda_aluno_repo=agenda_aluno_repo)





@router.get("/minhas_aulas", response_model=List[AgendaAulaResponseSchema], summary="[ALUNO] Buscar Minhas Aulas Agendadas por Período")
async def get_my_aulas_endpoint(
    start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    db_sql: Session = Depends(get_db),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    current_user: dict = Depends(auth_manager)
):
    if current_user.get("lv_acesso") not in ["aluno", "instrutor", "colaborador", "supremo"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    agenda_controller = AgendaController() 
    return await agenda_controller.get_my_aulas_by_period(
        start_date=start_date,
        end_date=end_date,
        current_user=current_user,
        db_session_sql=db_sql,
        agenda_repository=agenda_repo
    )

@router.get(
    "/aluno/{estudante_id}",
    response_model=List[AgendaAlunoResponse],
    summary="Listar agenda de aulas futuras e passadas de um estudante."
)
async def get_student_agenda_endpoint(
    estudante_id: int = Path(..., description="ID do estudante cuja agenda será consultada."),
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller),
    current_user: dict = Depends(auth_manager),
    start_date: Optional[date] = Query(None, description="Data de início (YYYY-MM-DD) para filtrar a agenda."),
    end_date: Optional[date] = Query(None, description="Data de fim (YYYY-MM-DD) para filtrar a agenda."),
):

    return await agenda_aluno_ctrl.get_student_agenda(
        estudante_id=estudante_id,
        current_user=current_user,
        agenda_aluno_repo=agenda_aluno_ctrl.agenda_repo,
        start_date=start_date,
        end_date=end_date
    )



@router.patch(
    "/presenca/{registro_id}",
    response_model=AgendaAlunoResponse,
    summary="Registrar presença ou falta de um estudante em uma aula (Debita a aula do contrato)."
)
async def update_status_presenca_endpoint(
    update_data: AgendaAlunoUpdate,
    registro_id: str = Path(..., description="ID do registro da agenda do aluno (Mongo Object ID)."),
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller),
    current_user: dict = Depends(auth_manager)
):
    updated_doc = await agenda_aluno_ctrl.update_status_presenca(
        registro_id=registro_id, 
        update_data=update_data,
        current_user=current_user
    )
    
    return AgendaAlunoResponse.model_validate(updated_doc)
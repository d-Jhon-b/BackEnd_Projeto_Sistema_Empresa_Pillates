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


@router.get("/cronograma", response_model=List[AgendaAulaResponseSchema], summary="Buscar Cronograma de Aulas por Período")
async def get_cronograma_endpoint(
    start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    current_user: dict = Depends(auth_manager) 
):
    id_teste=current_user.get('fk_id_estudio')
    # print(f'{id_teste}\n\n\n\n\n')
    return await agenda_controller.get_cronograma(
        start_date=start_date,
        end_date=end_date,
        agenda_repository=agenda_repo,
        current_user=current_user
    )

#-----------------------parte a repensar:
@router.delete("/aula/{aula_id}/estudante/{estudante_id}", 
               summary="Remover Estudante de uma Aula Específica (Desmatricular)")
async def unenroll_student_endpoint(
    aula_id: int,
    estudante_id: int,
    db_session: Session = Depends(get_db),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    agenda_aluno_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository),
    current_user: dict = Depends(auth_manager)
):
    """
    Remove um estudante da matrícula de uma aula, excluindo o registro em 
    SQL (Estudante_Aula), no array de participantes do Mongo Agenda Estúdio
    e o registro individual no Mongo Agenda Aluno.
    """
    return await aula_controller.unenroll_student_from_aula(
        aula_id=aula_id,
        estudante_id=estudante_id,
        current_user=current_user,
        db_session=db_session,
        agenda_repo=agenda_repo,
        agenda_aluno_repo=agenda_aluno_repo
    )




from fastapi import APIRouter, Depends, Query, Path, HTTPException, status,Form,UploadFile,File
from typing import List, Optional,Dict,Any
from datetime import date,datetime
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from src.database.dependencies import get_agenda_aluno_dependency, get_agenda_aulas_dependency, get_db 
from src.services.authService import auth_manager 
from src.controllers.agenda_aluno_controller import AgendaAlunoController 
from src.controllers.aula_controller import AulaController
from src.controllers.agenda_controller import AgendaController

from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository,AgendaAlunoUpdate
from src.repository.ContratoRepository import ContratoRepository 
from src.schemas.agenda_aluno_schemas import AgendaAlunoResponse,StatusPresencaEnum
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

# def get_agenda_aluno_controller(
#     db: Session = Depends(get_db),
#     agenda_aluno_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository)
# ) -> AgendaAlunoController:

#     return AgendaAlunoController(db_session=db, agenda_aluno_repo=agenda_aluno_repo)


def get_agenda_aluno_controller(
    db: Session = Depends(get_db),
    agenda_aluno_repo: AgendaAlunoRepository = Depends(get_agenda_aluno_repository),
    # ADICIONANDO A DEP. DO REPOSITÓRIO DE AULAS DO ESTÚDIO:
    agenda_aulas_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository) 
) -> AgendaAlunoController:
    # O AgendaAlunoController agora recebe o terceiro repositório
    return AgendaAlunoController(
        db_session=db, 
        agenda_aluno_repo=agenda_aluno_repo,
        agenda_aulas_repo=agenda_aulas_repo # Injetando
    )


@router.get("/minhas_aulas", response_model=List[AgendaAulaResponseSchema], summary="[ALUNO] ou [Professor] Buscar Minhas Aulas Agendadas por Período")
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
    "/detalhes_alunos/{aula_id}", 
    response_model=List[AgendaAlunoResponse], 
    summary="[PROFESSOR] Buscar AgendaAluno de todos os participantes de uma aula específica"
)
async def get_participants_agenda_details_endpoint(
    aula_id: int = Path(..., description="ID da Aula (Studio/SQL)"),
    class_date: date = Query(..., description="Data da aula (YYYY-MM-DD) para buscar os participantes"),
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller),
    agenda_aulas_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), 
    current_user: dict = Depends(auth_manager)
):
    # if current_user.get("lv_acesso") not in ["instrutor", "colaborador", "supremo"]:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas instrutores e administradores.")
        
    class_dt = datetime.combine(class_date, datetime.min.time())
    aula_agendada = await agenda_aulas_repo.find_aula_by_id_and_date(
        aula_id=aula_id, 
        date_time=class_dt
    )
    if not aula_agendada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Aula ID {aula_id} agendada para {class_date.isoformat()} não encontrada."
        )
    student_ids: List[int] = aula_agendada.get("participantes", [])
    if not student_ids:
        return [] 
    return await agenda_aluno_ctrl.get_students_agenda_by_ids(
        student_ids=student_ids, 
        class_date=class_date, 
        current_user=current_user
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
    summary="Registrar presença/falta e anexar fotos de evolução."
)
async def update_status_presenca_endpoint(
    status_presenca: Optional[StatusPresencaEnum] = Form(None), 
    nota_evolucao: Optional[str] = Form(None),

    anexos_files: Optional[List[UploadFile]] = File(None, description="Imagens de evolução para anexar."),
    
    registro_id: str = Path(..., description="ID do registro da agenda do aluno (Mongo Object ID)."),
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller),
    current_user: dict = Depends(auth_manager)
):
    update_data = AgendaAlunoUpdate(
        StatusPresenca=status_presenca, 
        NotaEvolucao=nota_evolucao
    )
    
    anexos_bytes: List[bytes] = []
    if anexos_files:
        for file in anexos_files:
            anexos_bytes.append(await file.read())

    updated_doc = await agenda_aluno_ctrl.update_status_presenca(
        registro_id=registro_id, 
        update_data=update_data,
        current_user=current_user,
        anexos_files_bytes=anexos_bytes 
    )
    
    return AgendaAlunoResponse.model_validate(updated_doc)




@router.delete("/admin/exclusao_total/{id_estudante}", status_code=status.HTTP_200_OK)
async def delete_student_agenda(
    id_estudante: int = Path(..., description="ID do estudante a ser excluído totalmente da agenda."),
    current_user: Dict[str, Any] = Depends(auth_manager),
    # USAMOS A DEPENDÊNCIA COMPLETA AGORA:
    agenda_aluno_ctrl: AgendaAlunoController = Depends(get_agenda_aluno_controller) 
) -> Dict[str, Any]:

    try:
        result = await agenda_aluno_ctrl.delete_student_agenda_data(
            id_estudante=id_estudante, 
            current_user=current_user
        )
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Erro inesperado no router ao deletar agenda do estudante {id_estudante}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erro interno do servidor ao processar exclusão de agendas do estudante."
        )
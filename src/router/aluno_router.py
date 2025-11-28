from fastapi import APIRouter, status, Depends, Query, Path
from sqlalchemy.orm import Session
from src.schemas.user_schemas import AlunoResponseName, AlunoCreatePayload, UserResponse, AlunoUpdatePayload
# from src.controllers.userController import UserController
from fastapi import HTTPException

from typing import List, Optional

from src.controllers.aluno_controller import AlunoController
from src.database.dependencies import get_db
from src.utils.authUtils import auth_manager

router = APIRouter(prefix="/alunos", tags=["Alunos"])
aluno_controller = AlunoController()



@router.post("/createAluno", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
summary="Criar novo aluno (Requer autenticação de Admin)"             
)
def create_aluno_endpoint(
    payload: AlunoCreatePayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aluno_controller.create_aluno(payload, current_user, db_session=db)


@router.get("/{user_id}", response_model=UserResponse, summary="Listar alunos por id(Requer autenticação de Admin)")
def get_aluno_by_id_endpoint(
    user_id:int,
    db:Session=Depends(get_db),
    current_user:dict=Depends(auth_manager)
):
    return aluno_controller.select_aluno_by_id(user_id=user_id, current_user=current_user, db_session=db)




@router.get("/", response_model=List[UserResponse], summary="Listar todos os alunos por estudio (Requer autenticação de Admin)")
def get_all_alunos_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager),
    studio_id: Optional[int] = Query(None,
    description="""
    - ID do estúdio para filtrar os colaboradores. 
    - Se omitido, o sistema usará o ID do estúdio do usuário logado.
    """
    )
    
):
    return aluno_controller.select_all_aluno_controller(
        studio_id=studio_id,
        current_user=current_user,
        db_session=db
    )



@router.patch("/alunos/{user_id}", 
    response_model=UserResponse, 
    status_code=status.HTTP_200_OK, 
    summary="Atualizar dados de um ALUNO (Requer Próprio Acesso ou Admin)"
)
def update_aluno_endpoint(
    update_data: AlunoUpdatePayload, 
    user_id: int = Path(..., description="ID do Aluno."),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):    
    return aluno_controller.update_aluno_data(
        user_id=user_id,
        update_data=update_data,
        current_user=current_user,
        db_session=db
    )


@router.get('/aluno-instrutor/{user_id}',
    # response_model=UserResponse, 
    response_model=AlunoResponseName, 
    status_code=status.HTTP_200_OK, 
    summary="Rota para instrutor buscar estudantes"            
)
def select_alunos_for_instrutor(
    estudante_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_manager)
):
    return aluno_controller.select_students_info_for_instrucotr(
        current_user=current_user,
        db_session=db,
        aluno_id=estudante_id
    )

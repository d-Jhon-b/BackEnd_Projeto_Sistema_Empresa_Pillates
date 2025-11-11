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
    prefix="/Chamada",
    tags=["Chamda"]
)


class ChamadaPostPayload:


    
    pass
@router.post(
    "/registrar-Presença",
    status_code=status.HTTP_200_OK,
       
)
def registrar_presenca(
payload: ChamadaPostPayload,
db: Session = Depends(get_db),
current_user: dict = Depends(auth_manager)
):
    return 
    
    
    pass
# user_controller = UserController()

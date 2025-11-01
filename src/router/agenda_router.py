# src/router/agenda_router.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorCollection

from src.database.dependencies import get_db, get_agenda_aulas_dependency 
from src.controllers.agenda_controller import AgendaController
from src.model.AgendaModel import AgendaAulaRepository
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from datetime import date
from typing import List

router = APIRouter(prefix="/agenda", tags=["Agenda e Cronograma (MongoDB)"])
agenda_controller = AgendaController()

def get_agenda_aula_repository(
    collection: AsyncIOMotorCollection = Depends(get_agenda_aulas_dependency) 
) -> AgendaAulaRepository:
    return AgendaAulaRepository(collection=collection)

def mock_current_user(): # Placeholder para autenticação
    return {"user_id": 1, "access_level": "supremo"} 

@router.post("/aula", response_model=AgendaAulaResponseSchema, status_code=status.HTTP_201_CREATED, summary="Agendar Nova Aula")
async def agendar_aula_endpoint(
    aula_data: AgendaAulaCreateSchema,
    db_sql: Session = Depends(get_db), 
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository), 
    current_user: dict = Depends(mock_current_user) 
):
    return await agenda_controller.create_new_aula(
        aula_data=aula_data,
        db_session_sql=db_sql,
        agenda_repository=agenda_repo
    )

@router.get("/cronograma", response_model=List[AgendaAulaResponseSchema], summary="Buscar Cronograma de Aulas por Período")
async def get_cronograma_endpoint(
    start_date: date = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data de fim (YYYY-MM-DD)"),
    agenda_repo: AgendaAulaRepository = Depends(get_agenda_aula_repository),
    current_user: dict = Depends(mock_current_user) 
):
    return await agenda_controller.get_cronograma(
        start_date=start_date,
        end_date=end_date,
        agenda_repository=agenda_repo
    )
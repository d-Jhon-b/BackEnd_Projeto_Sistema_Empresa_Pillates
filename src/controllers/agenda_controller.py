from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel 
from src.model.AgendaModel import AgendaAulaRepository
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from datetime import date, datetime
from typing import List, Dict, Any
from src.model.AulaModel import AulaModel

class AgendaController:
    
    # async def create_new_aula(
    #     self, 
    #     aula_data: AgendaAulaCreateSchema, 
    #     db_session_sql: Session, 
    #     agenda_repository: AgendaAulaRepository) -> AgendaAulaResponseSchema:
        
    #     user_model = UserModel(db_session=db_session_sql)
    #     professor_id = aula_data.fk_id_professor
    #     professor = user_model.select_user_id(professor_id) 
        
    #     if not professor:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    #             detail=f"Professor/Instrutor com ID {professor_id} não encontrado."
    #         )
        
    #     return await agenda_repository.create(aula_data)

    async def get_my_aulas_by_period(
        self, 
        start_date: date, 
        end_date: date, 
        current_user: Dict[str, Any], 
        db_session_sql: Session, 
        agenda_repository: AgendaAulaRepository
    ) -> List[AgendaAulaResponseSchema]:
        user_id = current_user.get("id_user")
        aula_model = AulaModel(db_session=db_session_sql)
        aulas_ids_do_estudante = aula_model.select_my_aulas(user_id) # Adapte o retorno deste método!

        if not aulas_ids_do_estudante:
            return [] # Nenhuma aula para este estudante
            
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # 3. Buscar agendamentos no MongoDB usando os IDs de Aula do SQL
        return await agenda_repository.find_by_aula_ids_and_period(aulas_ids_do_estudante, start_dt, end_dt)

    async def get_cronograma(self, start_date: date, end_date: date, agenda_repository: AgendaAulaRepository) -> List[AgendaAulaResponseSchema]:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        return await agenda_repository.find_by_period(start_dt, end_dt)
    
    async def create_new_cronograma(self, start_date: date, end_date: date, agenda_repository: AgendaAulaRepository) -> List[AgendaAulaResponseSchema]:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        pass
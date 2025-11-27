from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel 
from src.model.AgendaModel import AgendaAulaRepository
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from src.controllers.validations.permissionValidation import UserValidation
from datetime import date, datetime
from typing import List, Dict, Any
from src.model.AulaModel import AulaModel
from starlette.concurrency import run_in_threadpool # Adicionar esta importação
from src.controllers.utils.TargetUserFinder import TargetUserFinder
class AgendaController:

    async def get_cronograma(self, start_date: date, 
        end_date: date,                      
        agenda_repository: AgendaAulaRepository,
        current_user:dict
        ) -> List[AgendaAulaResponseSchema]:


        fk_id_estudio = current_user.get('fk_id_estudio')
        # fk_id_estudio = current_user.get('lv_acesso')
        # print(f'{fk_id_estudio}\n\n\n\n\n')
        # lv_acesso = current_user.get('lv_acesso')

        UserValidation._check_admin_permission(current_user)
        # user_estudio_id = current_user.get("fk_id_estudio")
        # print(f'{user_estudio_id}n\n\n\n\nn\n\n')
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        return await agenda_repository.find_by_period(start_dt, end_dt, id_estudio=fk_id_estudio)
    


    async def get_my_aulas_by_period(
        self, 
        start_date: date, 
        end_date: date, 
        current_user: Dict[str, Any], 
        db_session_sql: Session, 
        agenda_repository: AgendaAulaRepository
    ) -> List[AgendaAulaResponseSchema]:
        
        
        user_id = current_user.get("id_user")
        user_level = current_user.get("lv_acesso")
        is_instructor = user_level in ["instrutor", "colaborador", "supremo"]
        # print(is_instructor)
        UserValidation._check_all_permission(current_user)
        aula_model = AulaModel(db_session=db_session_sql)
        aulas_ids = await run_in_threadpool(
            aula_model.select_my_aulas, 
            user_id, 
            is_instructor 
        ) 

        if not aulas_ids:
            return [] 
            
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        return await agenda_repository.find_by_aula_ids_and_period(aulas_ids, start_dt, end_dt)
    

 
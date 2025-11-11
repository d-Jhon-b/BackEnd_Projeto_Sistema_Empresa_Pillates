from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from typing import List, Dict, Any
from datetime import datetime

class AgendaAulaRepository: 
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, aula: AgendaAulaCreateSchema) -> AgendaAulaResponseSchema:
        aula_data = aula.model_dump(by_alias=True, exclude_none=True)
        aula_data.pop('_id', None) 
        result = await self.collection.insert_one(aula_data)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return AgendaAulaResponseSchema.model_validate(created_doc)
        
    async def find_by_period(self, start_dt: datetime, end_dt: datetime) -> List[AgendaAulaResponseSchema]:
        query = {"dataAgendaAula": {"$gte": start_dt, "$lte": end_dt}}
        aulas_list = []
        async for doc in self.collection.find(query):
            aulas_list.append(AgendaAulaResponseSchema.model_validate(doc)) 
        return aulas_list
    
    async def find_by_aula_ids_and_period(self, aula_ids: List[int], start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
        """ Busca agendamentos no período que correspondem aos IDs de Aula SQL fornecidos. """
        query = {
            "fk_id_aula": {"$in": aula_ids},
            "dataAgendaAula": {"$gte": start_dt, "$lte": end_dt}
        }
        aulas_list = []
        async for doc in self.collection.find(query):
            aulas_list.append(AgendaAulaResponseSchema.model_validate(doc))
        return aulas_list
    
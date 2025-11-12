from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from typing import List, Dict, Any,Optional
from datetime import datetime

class AgendaAulaRepository: 
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection


    async def create(self, data: AgendaAulaCreateSchema) -> Dict[str, Any]:
        data_dict = data.model_dump(by_alias=True)
        try:
            result = await self.collection.insert_one(data_dict)
            # Recomenda-se buscar o documento criado para garantir a coerência
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return created_doc
        except Exception as e:
            print(f"ERRO MOTOR/MONGO: Falha ao inserir documento: {e}") 
            raise

    # async def create(self, aula: AgendaAulaCreateSchema) -> AgendaAulaResponseSchema:
    #     aula_data = aula.model_dump(by_alias=True, exclude_none=True)

    #     aula_data.pop('_id', None) 
    #     result = await self.collection.insert_one(aula_data)
    #     created_doc = await self.collection.find_one({"_id": result.inserted_id})
    #     return AgendaAulaResponseSchema.model_validate(created_doc)
        
    async def find_by_period(self, start_dt: datetime, end_dt: datetime) -> List[AgendaAulaResponseSchema]:
        query = {"dataAgendaAula": {"$gte": start_dt, "$lte": end_dt}}
        aulas_list = []
        async for doc in self.collection.find(query):
            aulas_list.append(AgendaAulaResponseSchema.model_validate(doc)) 
        return aulas_list
    
    async def find_by_aula_ids_and_period(self, aula_ids: List[int], start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
        """ Busca agendamentos no período que correspondem aos IDs de Aula SQL fornecidos. """
        query = {
            "AulaID": {"$in": aula_ids},
            "dataAgendaAula": {"$gte": start_dt, "$lte": end_dt}
        }
        aulas_list = []
        async for doc in self.collection.find(query):
            aulas_list.append(AgendaAulaResponseSchema.model_validate(doc))
        return aulas_list
    
    async def delete_by_aula_id(self, aula_id: int) -> bool:
        """ Deleta o agendamento no MongoDB usando o fk_id_aula (ID do SQL). """
        result = await self.collection.delete_one({"AulaID": aula_id})
        return result.deleted_count > 0
    

    async def update_by_aula_id(self, aula_id: int, data_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Atualiza campos específicos de um agendamento no MongoDB usando o fk_id_aula (ID do SQL).
        Retorna o documento atualizado ou None.
        """
        mongo_fields = {}

        if 'titulo_aula' in data_to_update:
            mongo_fields['disciplina'] = data_to_update['titulo_aula']

        if 'duracao_minutos' in data_to_update:
            mongo_fields['duracao_minutos'] = data_to_update['duracao_minutos']


        if 'data_aula' in data_to_update:
            mongo_fields['dataAgendaAula'] = data_to_update['data_aula']
        if 'desc_aula' in data_to_update:
            mongo_fields['descAgendaAula'] = data_to_update['desc_aula']
        if 'fk_id_professor' in data_to_update:
            mongo_fields['professorResponsavel'] = data_to_update['fk_id_professor']

        if 'fk_id_estudio' in data_to_update:
            mongo_fields['EstudioID'] = data_to_update['fk_id_estudio']


        if not mongo_fields:    
            return None 
        update_operation = {"$set": mongo_fields}
        
        result = await self.collection.find_one_and_update(
            {"AulaID": aula_id},
            update_operation,
            return_document=True 
        )
        return result
    
    async def add_participant(self, aula_id: int, participant_id: int) -> Optional[Dict[str, Any]]:
        """ Adiciona um ID à lista 'participantes_ids' no documento do MongoDB. """
        
        # Use $push para adicionar o ID se ele não existir
        update_result = await self.collection.find_one_and_update(
            {"AulaID": aula_id},
            {"$addToSet": {"participantes": participant_id}}, # $addToSet garante que não haverá duplicatas
            return_document=True # Retorna o documento atualizado
        )
        # print('funcionou')
        return update_result
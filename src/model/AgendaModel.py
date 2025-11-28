from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.agenda_schemas import AgendaAulaCreateSchema, AgendaAulaResponseSchema
from typing import List, Dict, Any,Optional
from datetime import datetime, timedelta
from bson import ObjectId 
from pymongo.errors import PyMongoError
import logging
from src.database.dependencies import MongoConnectionManager
import pytz 



#teste
import asyncio
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class AgendaAulaRepository: 
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection


    async def create(self, data: AgendaAulaCreateSchema) -> Dict[str, Any]:
        data_dict = data.model_dump(by_alias=True)
        try:
            result = await self.collection.insert_one(data_dict)
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return created_doc
        except Exception as e:
            print(f"ERRO MOTOR/MONGO: Falha ao inserir documento: {e}") 
            raise


    async def find_by_period(self, start_dt: datetime, end_dt: datetime, id_estudio: int) -> List[AgendaAulaResponseSchema]:
        # query = {"dataAgendaAula": {"$gte": start_dt, "$lte": end_dt}}
        query = {
            "dataAgendaAula": {"$gte": start_dt, "$lte": end_dt},
            "EstudioID": id_estudio 
        }
        # print(query)
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
    
    async def get_by_aula_id(self, aula_id: int) -> Optional[Dict[str, Any]]:

        try:

            document = await self.collection.find_one({"AulaID": aula_id}) 
            return document
        except Exception as e:
            # Trate erros de conexão ou busca aqui
            print(f"Erro ao buscar aula {aula_id} no MongoDB: {e}")
            return None
        
    async def update_by_aula_id(self, aula_id: int, data_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:

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
        
        update_result = await self.collection.find_one_and_update(
            {"AulaID": aula_id},
            {"$addToSet": {"participantes": participant_id}}, 
            return_document=True 
        )
        # print('funcionou')
        return update_result
    



    async def find_future_aulas_by_titulo(self, titulo_aula: str) -> List[Dict[str, Any]]:

        try:
            current_datetime = datetime.now()
            
            query = {
                "tituloAulaCompleto": titulo_aula,
                "dataAgendaAula": {"$gte": current_datetime} 
            }
            
            aulas = await self.collection.find(query).to_list(length=None)
            
            return aulas
        except Exception as e:
            print(f"Erro ao buscar aulas futuras por título: {e}")
            return []
    

    async def remove_student_from_all_aulas(self, estudante_id: int) -> int:
        """
        Remove o ID do estudante do array 'participantes' em todos os documentos de aula.
        Retorna a contagem de documentos modificados.
        """
        try:

            result = await self.collection.update_many(
                {"participantes": estudante_id}, 
                {"$pull": {"participantes": estudante_id}}
            )
            return result.modified_count
            
        except PyMongoError as err:
            logging.error(f'Erro ao remover estudante {estudante_id} dos participantes do AgendaAulas: {err}')
            return 0
        except Exception as err:
            logging.error(f'Erro geral ao processar remoção de participante no Mongo (AgendaAulas): {err}')
            return 0
        
    #-----------parte
    async def remove_participant(self, aula_id: int, participant_id: int) -> bool:
            update_result = await self.collection.find_one_and_update(
                {"AulaID": aula_id},
                {"$pull": {"participantes": participant_id}}, 
                return_document=False 
            )
            return update_result is not None
    #------------------não aplicado para produto final

    async def remove_participant_by_date(self, aula_id: int, participant_id: int, aula_date: datetime) -> bool:

        query = {
            "AulaID": aula_id,
            "dataAgendaAula": aula_date 
        }
        
        update_result = await self.collection.find_one_and_update(
            query,
            {"$pull": {"participantes": participant_id}}, 
            return_document=False 
        )
        return update_result is not None
    async def find_aula_by_titulo_and_date(
        self, 
        titulo_aula: str, 
        date_time: datetime
    ) -> Optional[Dict[str, Any]]:
        """ Busca uma ocorrência de aula pelo título e dentro do dia da data fornecida. """
        
        start_of_day = datetime.combine(date_time.date(), datetime.min.time())
        end_of_day = datetime.combine(date_time.date(), datetime.max.time())

        query = {
            "tituloAulaCompleto": titulo_aula,
            "dataAgendaAula": {"$gte": start_of_day, "$lte": end_of_day}
        }
        
        logging.debug(f"DEBUG_REPO_BUSCA_TITULO: Query busca por título e data: {query}")
        try:
            document = await self.collection.find_one(query) 
            logging.debug(f"DEBUG_REPO_BUSCA_TITULO: Documento encontrado: {document}")
            return document
        except PyMongoError as e:
            logging.error(f"Erro Mongo ao buscar aula '{titulo_aula}' na data {date_time.date()}: {e}")
            return None
        except Exception as e:
            logging.error(f"Erro geral ao buscar aula '{titulo_aula}' na data {date_time.date()}: {e}")
            return None

    async def find_aula_by_id_and_date(
        self, 
        aula_id: int, 
        date_time: datetime
    ) -> Optional[Dict[str, Any]]:

        start_of_day = datetime.combine(date_time.date(), datetime.min.time())
        end_of_day = datetime.combine(date_time.date(), datetime.max.time())
        
        query = {
            "AulaID": aula_id,
            "dataAgendaAula": {"$gte": start_of_day, "$lte": end_of_day}
        }
        
        try:
            document = await self.collection.find_one(query) 
            return document
        except PyMongoError as e:
            logging.error(f"Erro Mongo ao buscar aula {aula_id} na data {date_time.date()}: {e}")
            return None
        except Exception as e:
            logging.error(f"Erro geral ao buscar aula {aula_id} na data {date_time.date()}: {e}")
            return None
        

    async def find_next_enrolled_aula_date(self, aula_id: int, student_id: int) -> Optional[datetime]:
        UTC = pytz.utc
        utc_now = datetime.now(UTC) 
        
        cutoff_dt_utc = utc_now - timedelta(minutes=5)
        cutoff_dt_rounded = cutoff_dt_utc.replace(microsecond=0)
        
        query = {
            "AulaID": aula_id, 
            "participantes": student_id, 
            "dataAgendaAula": {"$gte": cutoff_dt_rounded}
        }
        

        logging.debug(f"DEBUG_REPO_INPUT: aula_id={aula_id}, student_id={student_id}")
        logging.debug(f"DEBUG_REPO_CUTOFF: Data de corte (Rounded UTC): {cutoff_dt_rounded!r}") 
        logging.debug(f"DEBUG_REPO_QUERY: Query de busca final: {query}")
        try:
            aula_cursor = self.collection.find(query).sort("dataAgendaAula", 1).limit(1)
            results = await aula_cursor.to_list(length=1) 
            aula_mongo = results[0] if results else None
            
            # logging.debug(f"DEBUG: Resultado da busca crua: {aula_mongo}\n\n\n\n\n")
                
        except Exception as e:
            logging.error(f'Erro fatal ao buscar próxima aula {aula_id} no Mongo: {e}', exc_info=True)
            return None
        
        if aula_mongo and aula_mongo.get("dataAgendaAula"):
            # Se entrar aqui, funcionou.
            return aula_mongo["dataAgendaAula"]
        
        return None   

    async def add_participant_by_date(self, aula_id: int, participant_id: int, aula_date: datetime):
        """
        Adiciona um participante em uma ocorrência de aula específica.
        """
        update_result = await self.collection.update_one(
            {
                "AulaID": aula_id,
                "dataAgendaAula": aula_date,
            },
            {
                "$addToSet": {"participantes": participant_id}
            }
        )
        return update_result.modified_count > 0 or update_result.matched_count > 0
    

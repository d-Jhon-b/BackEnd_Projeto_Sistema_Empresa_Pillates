from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse, AgendaAlunoUpdate
from typing import List, Dict, Any, Optional
from bson import ObjectId
import logging
from datetime import date, datetime
from src.repository.ContratoRepository import ContratoRepository 
from starlette.concurrency import run_in_threadpool 
from fastapi import HTTPException,status
from pymongo import ASCENDING, DESCENDING
# from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository 

class AgendaAlunoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    
    async def get_agenda_by_student_id(
        self, 
        estudante_id: int, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        
        query = {"EstudanteID": estudante_id}
        
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date

        if date_filter:
            # CORREÇÃO 2: Mudar "data_hora_aula" para "DataHoraAula"
            query["DataHoraAula"] = date_filter
            
        # CORREÇÃO 3: Mudar a ordenação para "DataHoraAula"
        cursor = self.collection.find(query).sort("DataHoraAula", ASCENDING)
        
        return await cursor.to_list(length=None)
    


    async def insert_registro(self, registro_data: Dict[str, Any]) -> Dict[str, Any]:

        registro_data["DataCriacao"] = datetime.now() 
        try:
            result = await self.collection.insert_one(registro_data)
            
            new_registro = await self.collection.find_one({"_id": result.inserted_id})
            return new_registro 
        except Exception as e:
            logging.error(f"Erro ao inserir registro no MongoDB: {e}")
            raise e  
        

        
        # except Exception as e:
        #     logging.error(f"Erro ao inserir registro no MongoDB: {e}")
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        #         detail="Falha ao inserir o registro de aula na agenda do aluno."
        #     )
        


    async def find_registros_by_aula_id(self, aula_id: int) -> List[Dict[str, Any]]:
        """Busca todos os alunos registrados para uma Aula (usado para checar presença/evolução)."""
        query = {"AulaID": aula_id}
        cursor = self.collection.find(query)
        return await cursor.to_list(length=None)

    async def find_registros_by_estudante_and_period(self, estudante_id: int, start_dt: datetime, end_dt: datetime) -> List[AgendaAlunoResponse]:
        """Busca a agenda de aulas de um estudante em um período."""
        query = {
            "EstudanteID": estudante_id,
            "DataHoraAula": {"$gte": start_dt, "$lte": end_dt}
        }
        registros = []
        async for doc in self.collection.find(query):
            registros.append(AgendaAlunoResponse.model_validate(doc))
        return registros


    async def update_registro(self, registro_id: str, update_data: AgendaAlunoUpdate) -> Optional[Dict[str, Any]]:
        try:
            obj_id = ObjectId(registro_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="O formato do ID do registro de aula para atualização é inválido."
            )

        data_to_set = update_data.model_dump(by_alias=True, exclude_none=True)
        
        if not data_to_set:
            return await self.collection.find_one({"_id": obj_id}) 

        updated_document = await self.collection.find_one_and_update(
            {"_id": obj_id},
            {"$set": data_to_set},
            return_document=True 
        )

        return updated_document
    
    # async def update_registro(self, registro_id: str, data_update: AgendaAlunoUpdate) -> Optional[Dict[str, Any]]:
    #     """
    #     Atualiza o status de presença de um registro da agenda do aluno no MongoDB.
    #     """
    #     # Converte o Pydantic model para um dicionário de atualização
    #     update_data = data_update.model_dump(exclude_none=True)
        
    #     if not update_data:
    #         return await self.select_registro_by_id(registro_id)

    #     try:
    #         update_result = await self.collection.update_one(
    #             {"_id": registro_id},
    #             {"$set": update_data}
    #         )

    #         if update_result.modified_count == 1:
    #             return await self.select_registro_by_id(registro_id)
    #         elif update_result.matched_count == 0:
    #             return None
    #         else:
    #             return await self.select_registro_by_id(registro_id)
    #     except Exception as e:
    #         logging.error(f"Erro ao atualizar registro {registro_id} no MongoDB: {e}")
    #         return None
    
    async def update_registro_detalhes(self, registro_id: str, data_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        try:
            object_id = ObjectId(registro_id) 
        except Exception:
            logging.warning(f"ID de registro inválido para update_registro_detalhes: {registro_id}")
            return None

        if "_id" in data_to_update:
            del data_to_update["_id"]
            
        if not data_to_update:
            return await self.select_registro_by_id(registro_id)

        update_operation = {"$set": data_to_update}
        updated_document = await self.collection.find_one_and_update(
            {"_id": object_id},
            update_operation,
            return_document=True 
        )
        if updated_document:
            updated_document["_id"] = str(updated_document["_id"])
            
        return updated_document


    async def find_future_aulas_by_titulo(self, titulo_aula: str) -> List[Dict[str, Any]]:
        current_datetime = datetime.now()
        query = {
            "tituloAulaCompleto": titulo_aula, 
            "dataAgendaAula": {"$gte": current_datetime}
        }
        aulas_cursor = self.collection.find(query)
        return await aulas_cursor.to_list(length=None)

    async def select_registro_by_id(self, registro_id: str) -> Optional[Dict[str, Any]]:

        try:
            obj_id = ObjectId(registro_id)
            registro = await self.collection.find_one({"_id": obj_id})
        
            return registro
        except Exception as e:
            # Log de erro específico do MongoDB
            logging.error(f"Erro ao buscar registro {registro_id} no MongoDB: {e}")
            return None
        

    async def delete_registro(self, registro_id: str) -> bool:
        
        try:
            object_id = ObjectId(registro_id)
        except:
            # Lidar com IDs inválidos (opcional, mas boa prática)
            return False 

        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
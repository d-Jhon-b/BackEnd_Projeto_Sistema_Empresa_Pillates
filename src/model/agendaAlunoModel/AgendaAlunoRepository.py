from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse, AgendaAlunoUpdate
from typing import List, Dict, Any, Optional
from bson import ObjectId
import logging
from datetime import date, datetime
from src.repository.ContratoRepository import ContratoRepository 
from starlette.concurrency import run_in_threadpool 
from fastapi import HTTPException,status

# from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository 

class AgendaAlunoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def insert_registro(self, registro_data: Dict[str, Any]) -> Dict[str, Any]:

        registro_data["DataCriacao"] = datetime.now() # Adiciona timestamp de criação
        
        try:
            # Insere o documento na coleção
            result = await self.collection.insert_one(registro_data)
            
            # Busca o documento inserido (incluindo o _id)
            new_registro = await self.collection.find_one({"_id": result.inserted_id})
            
            # O MongoDB retorna o _id como ObjectId; o find_one já o retorna
            # formatado ou mapeado para o formato do PyMongo.
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


    async def update_registro(self, registro_id: str, data_update: AgendaAlunoUpdate) -> Optional[Dict[str, Any]]:
        """
        Atualiza o status de presença de um registro da agenda do aluno no MongoDB.
        """
        # Converte o Pydantic model para um dicionário de atualização
        update_data = data_update.model_dump(exclude_none=True)
        
        if not update_data:
            return await self.select_registro_by_id(registro_id)

        try:
            update_result = await self.collection.update_one(
                {"_id": registro_id},
                {"$set": update_data}
            )

            if update_result.modified_count == 1:
                # Retorna o registro atualizado
                return await self.select_registro_by_id(registro_id)
            elif update_result.matched_count == 0:
                # O registro não foi encontrado para atualização
                return None
            else:
                # Retorna o registro existente se matched_count for 1 e modified_count for 0 (nenhuma mudança real)
                return await self.select_registro_by_id(registro_id)
        except Exception as e:
            logging.error(f"Erro ao atualizar registro {registro_id} no MongoDB: {e}")
            return None
    
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
            registro = await self.collection.find_one({"_id": registro_id})
        
            return registro
        except Exception as e:
            # Log de erro específico do MongoDB
            logging.error(f"Erro ao buscar registro {registro_id} no MongoDB: {e}")
            return None
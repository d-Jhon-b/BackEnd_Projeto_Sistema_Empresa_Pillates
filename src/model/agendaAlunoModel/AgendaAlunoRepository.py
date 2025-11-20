from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse, AgendaAlunoUpdate
from typing import List, Dict, Any, Optional
from bson import ObjectId
import logging
from datetime import date, datetime

class AgendaAlunoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_registro(self, data: AgendaAlunoCreate) -> Dict[str, Any]:
        """Cria um novo registro de aula/evolução na agenda do aluno."""
        data_dict = data.model_dump(by_alias=True)
        try:
            result = await self.collection.insert_one(data_dict)
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return created_doc
        except Exception as e:
            logging.error(f"ERRO MOTOR/MONGO: Falha ao inserir registro na Agenda do Aluno: {e}")
            raise

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
        """Atualiza o status de presença, nota de evolução ou anexos de um registro."""
        
        # Converte para Dicionário, usando alias=True se for Pydantic (ou by_alias=True no model_dump)
        update_dict = update_data.model_dump(by_alias=True, exclude_none=True)
        
        if not update_dict:
            return None 

        update_operation = {"$set": update_dict}
        
        try:
            object_id = ObjectId(registro_id)
        except:
             logging.error(f"ID de registro inválido: {registro_id}")
             return None
             
        result = await self.collection.find_one_and_update(
            {"_id": object_id},
            update_operation,
            return_document=True, # Retorna o documento atualizado
        )
        return result
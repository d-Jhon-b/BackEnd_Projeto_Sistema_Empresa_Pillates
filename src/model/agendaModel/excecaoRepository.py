from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

class ExcecaoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        
    async def insert_excecao(self, data: Dict[str, Any]) -> ObjectId:
        """ Insere uma nova exceção de cronograma (dia de folga/fechamento). """
        
        # Converte o objeto 'date' para 'datetime' para salvar no MongoDB
        if "dataExcecao" in data and isinstance(data["dataExcecao"], date):
            data["dataExcecao"] = datetime.combine(data["dataExcecao"], datetime.min.time())
            
        result = await self.collection.insert_one(data)
        return result.inserted_id

    async def find_excecoes_by_period(self, start_date: date, end_date: date, estudio_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """ Busca exceções (fechamentos) ativas em um período, opcionalmente filtrando por estúdio. """
        
        # Cria os objetos datetime de início e fim do período para a query MongoDB
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        query = {
            "dataExcecao": {
                "$gte": start_dt,
                "$lte": end_dt
            },
            # Busca apenas as exceções que ainda estão ativas (1 = Indisponível)
            "statusIndisponibilidade": 1
        }
        
        if estudio_id is not None:
            query["EstudioID"] = estudio_id

        cursor = self.collection.find(query)
        excecoes = await cursor.to_list(length=None)
        return excecoes

    async def update_excecao(self, excecao_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ Atualiza campos de uma exceção, usado para mudar descrição ou reverter status. """
        
        update_set = {}
        for key, value in update_data.items():
            if value is not None:
                update_set[key] = value

        if not update_set:
            return None 

        object_id = ObjectId(excecao_id)
        
        result = await self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_set},
            return_document=True 
        )
        return result
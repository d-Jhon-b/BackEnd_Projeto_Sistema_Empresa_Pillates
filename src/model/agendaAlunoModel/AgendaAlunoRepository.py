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
from pymongo.errors import PyMongoError, ConnectionFailure

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete, func
from src.model.aulaModel.aulaConfig import Aula, Estudante_Aula
from src.model.userModel.userConfig import Usuario
from src.model.planosModel.contratoConfig import Contrato
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.userModel.typeUser.aluno import Estudante
import logging
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
            logging.error(f"Erro ao buscar registro {registro_id} no MongoDB: {e}")
            return None
        

    async def delete_registro(self, registro_id: str) -> bool:
        try:
            object_id = ObjectId(registro_id)
        
        except PyMongoError as err:
            logging.error(f'Erro ao converter id de registro do mongo para tipo ObjectID.\nErro{err}')
            return False 
        except Exception as err:
            logging.error(f'Erro ao processar conversão de id do mongo para tipo ObjectID.\nErro{err}')
            return False 

        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
    
    async def delete_mongo_registro_estudante_by_id(self, id_estudante):
        try:
            result = await self.collection.delete_many({"EstudanteID": id_estudante})
            return result.deleted_count > 0
        
        except PyMongoError as err:
            logging.error(f'Erro ao processar remoção agendas do estudante com id {id_estudante}\nErro:{err}')
            return 0
        except Exception as err:
            logging.error(f'Erro ao processar alteração no Mongo\nErro:{err}')
            return 0 
    

    async def find_registros_by_multiple_students_and_period(
        self, 
        estudante_ids: List[int], 
        start_dt: datetime, 
        end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """
        Busca os registros de AgendaAluno para uma lista de estudantes em um período.
        """
        query = {
            "EstudanteID": {"$in": estudante_ids}, 
            "DataHoraAula": {"$gte": start_dt, "$lte": end_dt} 
        }
        
        registros: List[Dict[str, Any]] = []
        try:
            cursor = self.collection.find(query).sort("DataHoraAula", ASCENDING)
            
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                registros.append(doc)

            return registros
            
        except PyMongoError as err:
            logging.error(f'Erro Mongo ao buscar agendas para múltiplos estudantes: {err}')
            raise err
        except Exception as err:
            logging.error(f'Erro geral ao buscar agendas para múltiplos estudantes: {err}')
            raise err


    #------------------não aplicado para produto final
    async def delete_registro_by_estudante_and_aula(self, estudante_id: int, aula_id: int) -> bool:
        try:
            result = await self.collection.delete_one({
                "EstudanteID": estudante_id,
                "AulaID": aula_id
            })
            return result.deleted_count > 0
        except PyMongoError as err:
            logging.error(f'Erro Mongo ao deletar registro (EstudanteID: {estudante_id}, AulaID: {aula_id}): {err}')
            return False
    #------------------não aplicado para produto final

    """
    Método apenas para excluir registros no Banco de dados SQl.
    Motivo peloq qual estou misturando com o repository para acessar o mongo:
    "Seria problematico criar um novo arquivo e classe para armazenar uma única função ou duas,
    pretendo manter esse método aqui por hora, dado que o prazo está curto...
    A parte ruim é ter q chamar todas as Configs do Banco relacionadas com esse tipo de aplicação... 
    deprimente, mas é o que temos para hj.
    "

    """
    def delete_sql_registro_aula_estudante_by_id(self, id_estudante:int, session_db:Session):
        try:
            stmt = delete(Estudante_Aula).where(Estudante_Aula.fk_id_estudante == id_estudante)
            res_delete = session_db.execute(stmt)
            deleted_count = res_delete.rowcount
            session_db.commit()
            if deleted_count > 0:
                logging.info(f'Sucesso ao excluir {deleted_count} registros do estudante {id_estudante} no SQL.')
                return True 
            else:
                logging.warning(f'Nenhum registro encontrado para exclusão para o estudante {id_estudante} no SQL.')
                return True  
            
        except SQLAlchemyError as err:
            logging.error(f'Erro ao aplicar remoção de registro do estudante de id:{id_estudante}\n\nErro:{err}')
            session_db.rollback()
            return None
    
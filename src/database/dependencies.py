from src.database.connPostGreNeon import CreateSessionPostGre

from src.database.connMongo import MongoConnectionManager 
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Generator, Callable
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

def get_db():
    """
    Função de dependência do FastAPI para obter uma sessão de banco de dados.
    Usa 'yield' para garantir que a sessão seja fechada após a requisição.
    """
    db_session_creator = CreateSessionPostGre()
    session = db_session_creator.get_session()
    try:
        yield session 
    finally:
        session.close() 


def create_mongo_collection_dependency(collection_name: str) -> Callable[[], Generator]:
    def get_mongo_collection() -> Generator[AsyncIOMotorCollection, None, None]:
        try:
            client = MongoConnectionManager.get_client()
            db = client.get_database(MongoConnectionManager.DB_NAME)
            yield db[collection_name] 

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro ao acessar coleção MongoDB: {collection_name}"
            )
    return get_mongo_collection

# Injetor para a coleção 'AgendaAulas'
get_agenda_aulas_dependency = create_mongo_collection_dependency("AgendaAulas")
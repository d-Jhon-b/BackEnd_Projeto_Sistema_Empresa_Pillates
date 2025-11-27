# src/database/connMongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status
from typing import Optional
from src.database.modelConfig.configMongo import MongoParamBuilder 
import logging
class MongoConnectionManager:
    client: Optional[AsyncIOMotorClient] = None
    DB_NAME: str = "" 

    @classmethod
    async def connect(cls):
        try:
            builder = MongoParamBuilder()
            config = builder.config
        except Exception as e:
            print(f"ERRO DE CONFIGURAÇÃO DO AMBIENTE MONGODB: {e}")
            raise RuntimeError(f"Falha ao carregar as variáveis de ambiente do MongoDB: {e}") 
        
        MONGO_URI = config.mongo_uri
        cls.DB_NAME = config.mongo_db_name 

        try:
            cls.client = AsyncIOMotorClient(MONGO_URI)
            await cls.client.admin.command('ping') 
            # print(f"MongoConnectionManager: Cliente MongoDB Atlas ativo (DB: {cls.DB_NAME}).")
            logging.info(f"MongoConnectionManager: Cliente MongoDB Atlas ativo (DB: {cls.DB_NAME}).")
        except Exception as e:
            cls.client = None
            import traceback
            traceback.print_exc()
            print(f"ERRO FATAL ao conectar ao MongoDB Atlas: {e}")
            raise Exception(f"Falha na conexão com MongoDB: {e}") 
        

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            cls.client = None
            
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
         if not cls.client:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Cliente MongoDB não está ativo. Falha no Startup."
            )
         return cls.client
    

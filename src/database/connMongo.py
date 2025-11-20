# src/database/connMongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status
from typing import Optional
from src.database.modelConfig.configMongo import MongoParamBuilder 

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
            print(f"MongoConnectionManager: Cliente MongoDB Atlas ativo (DB: {cls.DB_NAME}).")
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
    

# if __name__ == "__main__":
#     import asyncio
    
#     async def test_connection():
#         print("\n--- 🧪 Teste de Conexão Direta ao MongoDB Atlas ---")
#         try:
#             # Tenta conectar
#             await MongoConnectionManager.connect()
            
            
            
#             print("\n SUCESSO! A conexão com o MongoDB Atlas foi estabelecida com sucesso.")
            
#         except Exception as e:
#             # Se a conexão falhar, o erro detalhado será impresso pelo método connect()
#             print("\n FALHA: Não foi possível estabelecer a conexão com o MongoDB Atlas.")
#             # O detalhe exato do erro deve ter sido impresso acima
            
#         finally:
#             # Garante que a conexão seja fechada após o teste
#             await MongoConnectionManager.close()
#             print("Conexão fechada.")
            
#     # Executa a função assíncrona
#     asyncio.run(test_connection())
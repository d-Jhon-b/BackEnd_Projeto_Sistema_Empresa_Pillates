# from psycopg2 import connect, OperationalError, Error
# from psycopg2.extensions import connection
from pydantic import BaseModel, ValidationError
from time import sleep
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager


from typing import Optional, Dict, Union
from src.database.modelConfig.dbModel import dbModel
from src.database.modelConfig.configPostGre import PostGreParamBuilder


class PostGreModel(dbModel):
    def __init__(self):
        self.env_data = PostGreParamBuilder()
        self.connection_url = self.env_data.build_data_env()


        #self.conn = None
        self.engine = None
        self.AsyncSessionLocal = None
        self.is_setup = False        
        
        print("Modelo de Conexão PostGre Síncrono inicializado.")


    def connect_db(self):
        ...
    def diconnect_db(self):
        ...

    def setup_engine(self)->None:
        if self.is_setup:
            print(f'Engine PostGreSQL já está configurada')
            return
        url_for_log = self.connection_url.split("@")[-1]
        print(f'Configurando Engine PostGreSQL com a URL: {url_for_log}')

        #cria engine Async:
        self.engine = create_async_engine(
            self.connection_url,
            echo=False,
            pool_pre_ping = True
        )
        self.AsyncSessionLocal = sessionmaker(
            autocommit= False,
            autoflush=False,
            bind= self.engine,
            class_=AsyncSession,
            expire_on_commit=False
           )
        

        self.is_setup = True
        print(f'Configuração do Engine PostRe concluido...')

    async def disconnect_db(self):

        if self.engine:
            print('Encerrando pool de conexões do Engine...')
            await self.engine.dispose()
            print('Pool de conexões encerrado.')
        else:
            print('Engine não configurado para encerrar.')


POSTGRE_DB_CONNECTOR = PostGreModel()

@asynccontextmanager
async def get_postgre_session() -> AsyncGenerator[AsyncSession, None]:
    if not POSTGRE_DB_CONNECTOR.is_setup:
         # Idealmente, o setup_engine deve ser chamado no startup do FastAPI.
         raise ConnectionError("O Engine do PostGreSQL deve ser configurado.")
         
    # Usa a fábrica de sessões do objeto global
    async with POSTGRE_DB_CONNECTOR.AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() 
        except Exception:
            await session.rollback() 
            raise


if __name__ == '__main__':
    import asyncio
    from sqlalchemy import text
    
    async def run_simple_test():
        
        # 1. Configurar o Engine
        POSTGRE_DB_CONNECTOR.setup_engine() 
        print("Engine configurado. Tentando obter sessão...")
        
        # 2. Chamar a função de dependência para obter a sessão
        async with get_postgre_session() as session:
            
            # 3. Executar a consulta
            result = await session.execute(text("SELECT version()"))
            version_info = result.scalar_one() 
            
            print("\n-------------------------------------------")
            print(f"✅ CONEXÃO BEM-SUCEDIDA!")
            print(f"Versão do PostgreSQL: {version_info}")
            print("-------------------------------------------")
            
        # 4. Encerra o Engine
        await POSTGRE_DB_CONNECTOR.disconnect_db()

    # Executar a função assíncrona
    asyncio.run(run_simple_test())
        

# try:
#     postLink = PostGreModel()
#     conn = postLink.connect_db()
#     cursor = conn.cursor()
#     cursor.execute('select version()')
#     res = cursor.fetchone()
#     print(res)
# except Exception as err:
#     print(f'{err}')


from typing import Optional
from pydantic import BaseModel, ValidationError

from src.database.envConfig.envPostGre import EnvLoaderPostGre

class PostGreConfig(BaseModel):
    database:str
    host:str
    user:str
    password:str
    port:str
    #para o modelo asyncrono do FastAPI
    driver: str = 'asyncpg'

class PostGreParamBuilder():
    def __init__(self):
        self.env_loader = EnvLoaderPostGre()
        self.config_data = self.env_loader.get_config()
        self.config_data_lower = {key.lower(): value for key, value in self.config_data.items()}
        try:
            self.config = PostGreConfig(**self.config_data_lower)
        except ValidationError as err:
            raise ValueError(f'Variáveis de ambiente do PostGe faltando: {err}')
        
    def build_data_env(self)->dict:
        # self.data_env = {
        #     "database": self.config.database, 
        #     "user": self.config.user,
        #     "password": self.config.password,
        #     "host": self.config.host,
        #     "port": self.config.port,
        #     "DRIVER": self.config.driver
            
        #     }

        self.url_connection = (
            f"postgresql+{self.config.driver}://"
            f"{self.config.user}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/"
            f"{self.config.database}"
        )    
        print(f"URL Async (App): {self.url_connection}")
        return  self.url_connection
    
    def build_sync_url_for_alembic(self) -> str:
        """
        Constrói a URL de conexão SÍNCRONA, específica para o Alembic.
        """
        sync_driver = "psycopg2"
        url_connection = (
            f"postgresql+{sync_driver}://"  # Força o uso do driver síncrono
            f"{self.config.user}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/"
            f"{self.config.database}"
        )
        print(f"URL Sync (Alembic): {url_connection}")
        return url_connection


# param = PostGreParamBuilder()
# build = param.build_data_env()

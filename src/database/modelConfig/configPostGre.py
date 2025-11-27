from typing import Optional
from pydantic import BaseModel, ValidationError

from src.database.envConfig.envPostGre import EnvLoaderPostGre

class PostGreConfig(BaseModel):
    database:str
    host:str
    user:str
    password:str
    port:str
    url_neon:str

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
        data_env = {
            "database": self.config.database, 
            "user": self.config.user,
            "password": self.config.password,
            "host": self.config.host,
            "port": self.config.port
            }
        return data_env
    
    # def build_url_env(self)->Optional[str]:
    #     self.url_postGre_local = (
    #         f"postgresql://{self.config.user}:"
    #         f"{self.config.password}@{self.config.host}:"
    #         f"{self.config.port}/{self.config.database}"
    #     )
    #     return str(self.url_postGre_local)
    
    def build_url_env(self)->Optional[str]:
        self.url_postGre_neon = self.config.url_neon

        return str(self.url_postGre_neon)
    


# src/database/modelConfig/configMongo.py (MUDE ESTE ARQUIVO)
from typing import Optional, Union, Dict
from pydantic import BaseModel, ValidationError, Field # Importe Field
from src.database.envConfig.envMongo import EnvLoaderMongo


class MongoConfig(BaseModel):
    mongo_uri: str = Field(alias="MONGO_URI") 
    mongo_user: Optional[str] = Field(alias="MONGO_USER")
    mongo_password: Optional[str] = Field(alias="MONGO_PASSWORD")
    mongo_db_name: str = Field(alias="MONGO_DB_NAME") # <--- Mapeamento explícito


class MongoParamBuilder():
    def __init__(self):
        self.env_loader = EnvLoaderMongo()
        self.config_data = self.env_loader.get_config()
        
        try:
            self.config = MongoConfig(**self.config_data) 
        except ValidationError as err:
            raise ValueError(f'Variáveis de ambiente do MongoDB faltando:\n{err}')
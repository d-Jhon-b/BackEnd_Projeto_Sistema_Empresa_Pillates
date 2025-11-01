# src/database/modelConfig/configMongo.py (MUDE ESTE ARQUIVO)
from typing import Optional, Union, Dict
from pydantic import BaseModel, ValidationError, Field # Importe Field
from src.database.envConfig.envMongo import EnvLoaderMongo


class MongoConfig(BaseModel):
    # Usando Field(alias=...) para mapear as chaves MAIÚSCULAS do .env
    mongo_uri: str = Field(alias="MONGO_URI") 
    mongo_user: Optional[str] = Field(alias="MONGO_USER")
    mongo_password: Optional[str] = Field(alias="MONGO_PASSWORD")
    mongo_db_name: str = Field(alias="MONGO_DB_NAME") # <--- Mapeamento explícito

    # Remova o bui_data_env, pois ele não é mais necessário e complicava o fluxo.
    # ... (remova ou comente o bui_data_env)

class MongoParamBuilder():
    def __init__(self):
        self.env_loader = EnvLoaderMongo()
        self.config_data = self.env_loader.get_config()
        
        try:
            # Passa o dict original (chaves MAIÚSCULAS), Pydantic usa o alias
            self.config = MongoConfig(**self.config_data) 
        except ValidationError as err:
            raise ValueError(f'Variáveis de ambiente do MongoDB faltando:\n{err}')
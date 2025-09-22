from typing import Optional, Union, Dict
from pydantic import BaseModel
from pydantic import BaseModel, ValidationError

from src.database.envConfig.envMongo import EnvLoaderMongo


class MongoConfig(BaseModel):
    mongo_uri:str
    mongo_user: Optional[str]
    mongo_password:Optional[str]


class MongoParamBuilder():
    def __init__(self):
        self.env_loader = EnvLoaderMongo()
        self.config_data = self.env_loader.get_config()
        self.config_data_loewr = {chave.lower(): valor for chave, valor in self.config_data.items()}
        try:
            self.config = MongoConfig(**self.config_data_loewr)
        except ValidationError as err:
            raise ValueError(f'Variáveis de ambiente do MongoDB faltando:\{err}')

    def buil_data_env(self) -> dict:
        data_env = {
            "host": self.config.mongo_uri,
            # Se o usuário e a senha existirem vai colocar no dicionário
            **({'username': self.config.mongo_user} if self.config.mongo_user else {}),
            **({'password': self.config.mongo_password} if self.config.mongo_password else {})
        }
        return data_env
    
# try:
#     mongoBuilder = MongoParamBuilder()
#     mongoRes = mongoBuilder.buil_data_env()
#     print(mongoRes)
# except:
#     print("erro ao buscar dados")

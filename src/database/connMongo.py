from pymongo import MongoClient, errors
from pydantic import BaseModel, ValidationError

from typing import Optional, Dict, Union
from src.database.modelConfig.dbModel import dbModel

from src.database.envConfig.envMongo import EnvLoaderMongo


class MongoConfig(BaseModel):
    mongo_uri:str
    mongo_user: Optional[str]
    mongo_password:Optional[str]

class MongoModel(dbModel):
    def __init__(self):
        self.env_loader=EnvLoaderMongo()
        self.configMongo=self.env_loader.get_config()

        self.configMongo_lower = {chave.lower(): valor for chave, valor in self.configMongo.items()}

        try:
            self.config=MongoConfig(**self.configMongo_lower)
        except ValidationError as err:
            raise ValueError(f'Uma ou mais variáveis de ambiente para a conexão com o mongoDB está faltando.\nErro de validação{err}')
        self.connMongo=None

    def connect_db(self)->Union[MongoClient, str]:
        return
        # try:
        #     self.host = self.config.mongo_uri.replace()
        #     self.connMongo = MongoClient()    
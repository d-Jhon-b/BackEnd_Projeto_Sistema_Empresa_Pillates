from pymongo import MongoClient, errors
from typing import Optional, Dict, Union
from src.database.modelConfig.dbModel import dbModel

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


from src.database.envConfig.envMongo import EnvLoaderMongo
from src.database.modelConfig.configMongo import MongoParamBuilder



class MongoModel(dbModel):
    def __init__(self):
        self.env_data = MongoParamBuilder()
        self.parametros = self.env_data.buil_data_env()
        self.client = None

    def connect_db(self)->Union[MongoClient, str]:
        if self.client:
            print("COonxão com Mongo já está ativa.")
            return self.client
        try:
            self.client = MongoClient(**self.parametros)
            # self.res = self.client.admin.command('ping')  
            # return self.res
            return self.client
        except (ConnectionFailure, ServerSelectionTimeoutError) as err:
            return f'Erro ao conectar ao banco de dados:\n {err}'
        except Exception as err:
            return f'Erro inesperado na conexão:\n {err}'

    def diconnect_db(self):
        if self.client and not self.client.close():
            self.client.close()
        # return f"Errro"
    

# try:
#     mongoModel = MongoModel()
#     res = mongoModel.connect_db()
#     question = res.admin.command('ping')

#     print(question)
# except errors.ConnectionFailure as err: 
#     print(f"Erro{err}")
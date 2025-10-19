from psycopg2 import connect, OperationalError, Error
from psycopg2.extensions import connection
from pydantic import BaseModel, ValidationError


from typing import Optional, Dict, Union
from src.database.modelConfig.dbModel import dbModel
from src.database.modelConfig.configPostGre import PostGreParamBuilder


# from src.database.envConfig.envPostGre import EnvLoaderPostGre

# class PostGreConfig(BaseModel):
#     database:str
#     host:str
#     user:str
#     password:str
#     port:str



class PostGreModel(dbModel):
    def __init__(self):
        self.env_data = PostGreParamBuilder()
        self.parametros = self.env_data.build_data_env()
        self.conn = None


    def connect_db(self)->Union[connection, str]:
        if self.conn and not self.conn.closed:
            print(f'Conexão já está ativa')
            return self.conn
        try:
            self.conn = connect(**self.parametros)
            return self.conn
        except OperationalError as err:
            raise OperationalError(f'Erro ao conectar ao banco de dados PostGreSQL.\nERRO:{err}')

    def diconnect_db(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

            

        

# try:
#     postLink = PostGreModel()
#     conn = postLink.connect_db()
#     cursor = conn.cursor()
#     cursor.execute('select version()')
#     res = cursor.fetchone()
#     print(res)
# except Exception as err:
#     print(f'{err}')
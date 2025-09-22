from psycopg2 import connect, OperationalError, Error
from psycopg2.extensions import connection
from pydantic import BaseModel, ValidationError


from typing import Optional, Dict, Union
from src.database.modelConfig.dbModel import dbModel

from src.database.envConfig.envPostGre import EnvLoaderPostGre

class PostGreConfig(BaseModel):
    database:str
    host:str
    user:str
    password:str
    port:str



class PostGreModel(dbModel):
    def __init__(self):
        self.env_loader = EnvLoaderPostGre()
        self.configPostGre = self.env_loader.get_config()    
        # if not all(configPostGre.values()):
        self.configPostGre_lower = {k.lower(): v for k, v in self.configPostGre.items()}
        try:
            self.config=PostGreConfig(**self.configPostGre_lower)
        except ValidationError as e:
            raise ValueError(f"Uma ou mais variáveis de ambiente para a conexão com o Postgre está faltando. \nErro de validação: {e}")
        self.conn=None


    def connect_db(self)->Union[connection, str]:
        if self.conn and not self.conn.closed:
            print(f'Conexão já está ativa')
            return self.conn
        try:
            self.conn = connect(
            dbname=self.config.database,
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port                                            
            )
            # self.cursor = self.conn.cursor()
            # self.connectionValues ={
            #     "connection": self.conn,
            #     "cursor":self.cursor
            # }
            # return self.connectionValues
            return self.conn
        except OperationalError as err:
            raise OperationalError(f'Erro ao conectar ao banco de dados PostGreSQL.\nERRO:{err}')

    def diconnect_db(self):
            # self.teste =self.connectionValues["connection"]
            if self.conn and not self.conn.closed:
                self.conn.close()

            

        

try:
    db_instance = PostGreModel()
    
    # 6. Chama o método de instância na instância
    sql_conn = db_instance.connect_db()
    
    # 7. Usa o objeto de conexão para criar um cursor
    cursor = sql_conn.cursor()
    
    print("Cursor criado com sucesso!")

    # Exemplo de consulta
    cursor.execute("SELECT version();")
    print("Versão do banco de dados:", cursor.fetchone())

    # Lembre-se de fechar a conexão no final
    cursor.close()
    sql_conn.close()
    print("Conexão encerrada.")
except Exception as err:
    print(f'{err}')
from src.database.envConfig.getEnv import EnvLoader
from typing import Optional

class EnvLoaderMongo(EnvLoader):
    def __init__(self):
        super().__init__("mongoDB.env")
    def get_config(self)->dict[str, Optional[str]]:
        self._load()
        return self._get_all(["MONGO_URI", "MONGO_USER", "MONGO_PASSWORD"])
# try:
#     envLoad = EnvLoaderMongo()
#     envLoader = envLoad.get_config()
#     print(envLoader)

# except Exception as err:
#     print('Erro ao carreagar .env',{err})

from src.database.envConfig.getEnv import EnvLoader
from typing import Optional

class EnvLoaderMongo(EnvLoader):
    def __init__(self):
        super().__init__("mongoDB.env")
    def get_config(self)->dict[str, Optional[str]]:
        self._load()
        # Incluindo MONGO_DB_NAME e MONGO_CLUSTER_URL na lista de chaves a carregar
        return self._get_all([
            "MONGO_URI", 
            "MONGO_USER", 
            "MONGO_PASSWORD", 
            "MONGO_DB_NAME"
        ])
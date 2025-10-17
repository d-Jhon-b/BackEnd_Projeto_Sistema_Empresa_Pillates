from src.database.envConfig.getEnv import EnvLoader
from typing import Optional

class EnvLoaderPostGre(EnvLoader):
    def __init__(self):
        super().__init__("postGre.env")



    def get_config(self)->dict[str, Optional[str]]:
        self._load()
        return self._get_all(["DATABASE", "HOST", "USER", "PASSWORD", "PORT", "URL_NEON"])



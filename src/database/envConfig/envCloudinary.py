from src.database.envConfig.getEnv import EnvLoader
from typing import Optional, Dict, List

class EnvCloudinary(EnvLoader):

    def __init__(self):
        super().__init__("cloudinary.env")
        
    def get_config(self) -> Dict[str, Optional[str]]:
        self._load()
        keys_to_load: List[str] = [
            "CLOUDINARY_CLOUD_NAME", 
            "CLOUDINARY_API_KEY", 
            "CLOUDINARY_API_SECRET"
        ]
        config_data = self._get_all(keys_to_load)        
        for key in keys_to_load:
            if config_data.get(key) is None:
                raise ValueError(f"A variável '{key}' é obrigatória e não foi encontrada.")
        
        return config_data
    
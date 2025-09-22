from dotenv import load_dotenv
from pathlib import Path
from typing import Union, Optional
from abc import abstractmethod, ABC
import os
from src.database.modelConfig.envModel import BaseEnvLoader


class EnvLoader(BaseEnvLoader):
    def __init__(self, filename:str):
        # self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        # self.env_path = self.project_root / "config" / filename

        self.env_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / filename


        self.env_loaded = False
        self.variables: dict[str, Optional[str]] = {}

    def _load(self)->bool:
        if not self.env_path.exists():
            raise FileNotFoundError(f'Arquivo .env não encontrado: {self.env_path}')
        self.env_loaded = load_dotenv(self.env_path)
        if not self.env_loaded:
            raise EnvironmentError(f"Não foi possivel carregar o .env:\n{self.env_path}")
        return self.env_loaded
    
    def _get_variable(self, key:str)->Optional[str]:
        if not self.env_loaded:
            raise RuntimeError(f'Variáveis .env não carregadas. Chame `.load` primeiro')
        return os.getenv(key)
    
    def _get_all(self, keys:list[str])->dict[str,Optional[str]]:
        return {key: self._get_variable(key) for key in keys}
        
    def get_config(self)->dict[str, Optional[str]]:
        ...

from abc import ABC, abstractmethod
from typing import Optional



class BaseEnvLoader(ABC):
    def __init__(self, filename:str):
        self.filename=filename
        self.env_loaded = False

    #Uma classe abstrata para caber nos arquivos: envMongo.py e envPostGre.py.
    #Isso vai acontecer pela herança
    @abstractmethod
    def get_config(self)->dict[str,Optional[str]]:
        pass

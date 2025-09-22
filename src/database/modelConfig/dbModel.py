from abc import ABC, abstractmethod
from typing import Optional, Any    

class dbModel(ABC):
    @abstractmethod
    def connect_db(self)->Optional[Any]:
        pass
    @abstractmethod
    def diconnect_db(self)->None:
        pass


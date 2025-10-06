from pydantic import BaseModel, Field
from typing import Union, Optional, Any
from enum import Enum
from bson import ObjectId
from datetime import date


class AdmPlusConfig(BaseModel):
    idAdmPlus: Optional[int] = Field(None, title='Id para o banco de dados')
    fkIdUser: Optional[int] = Field(..., title='chave estrangeira da sua classe e tabela do python e banco de dados respectivamente')

class AdmConfig(BaseModel):
    idAdm: Optional[int] = Field(None, title='Id para o banco de dados')
    fkIdUser: Optional[int] = Field(..., title='chave estrangeira da sua classe e tabela do python e banco de dados respectivamente')

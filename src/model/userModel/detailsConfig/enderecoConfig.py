from pydantic import BaseModel, Field
from typing import Union, Sequence, Optional, Any, Dict
from enum import Enum

class TipoEndreco(str, Enum):
    RESIDENCIAL= 'RESIDENCIAL'
    COMERCIAL='COMERCIAL'

class EnderecoConfig(BaseModel):
    id_user: Optional[int]= Field(None, title='ID para o banco de dados')
    fk_id_user: Optional[int]=Field(None, title='ID estrangeira da tabela usuario')
    tipo_endereco: TipoEndreco = Field(..., title='Tipo de endereço do usuario')
    endereco:str = Field(..., title='Endereço do usuario')
    cep: str=Field(..., title='Cep do usuario')
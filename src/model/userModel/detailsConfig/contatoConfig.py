from pydantic import BaseModel, Field
from typing import Union, Sequence, Optional, Any, Dict
from enum import Enum

class TipoContato(str, Enum):
    RESIDENCIAL = 'RESIDENCIAL'
    COMERCIAL='COMERCIAL'
    FAMILIAR='FAMILIAR'

class contatoConfig(BaseModel):
    id_contato:Optional[int] =Field(None, title='id do contato')
    fk_id_user: Optional[int]=Field(None,title='ID estrangeira da tabela user')
    tipo_contato: TipoContato=Field(..., title='Tipo do contato do usuário' )
    numero_contato: str=Field(..., title='Numero do contato')
from pydantic import BaseModel, Field
from typing import Union, Sequence, Optional, Any, Dict
from enum import Enum


class TipoEmail(str, Enum):
    PESSOAL = 'PESSOAL'
    COMERCIAL= 'COMERIAL'
# sa.Column('tipo_email',sa.Enum('PESSOAL', 'COMERCIAL', name='tipo_email_enum'), nullable=False),

class EmailConfig(BaseModel):
    id_email: Optional[int]=Field(None, title='Id da tabela email')
    fk_id_user: Optional[int]= Field(None, title='id estrangeira da tabela user')
    tipo_email: TipoEmail=Field(..., title='tipo do email')
    endereco_email: Optional[str]=Field(..., title='Email do usuario')
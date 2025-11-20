from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class MetodoPagamentoEnum(str, Enum):
    CARTAO = "cartao"
    PIX = "pix"
    DINHEIRO = "dinheiro"

class PagamentoBase(BaseModel):
    valor_pagamento: Decimal
    data_vencimento: datetime
    metodo_pagamento: Optional[str]
    status_pagamento: str
    descricao_pagamento: str
    
class PagamentoResponse(PagamentoBase):
    id_pagamento: int
    fk_id_contrato: Optional[int]
    fk_id_estudante: int
    data_pagamento: Optional[datetime] 
    class Config:
        from_attributes = True 


class PagamentoInput(BaseModel):

    metodo: MetodoPagamentoEnum
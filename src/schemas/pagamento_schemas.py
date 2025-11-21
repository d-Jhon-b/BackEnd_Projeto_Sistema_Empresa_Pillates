from pydantic import BaseModel,Field
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



class PagamentoOut(BaseModel):
    id_pagamento: int
    fk_id_contrato: Optional[int] = None
    fk_id_estudante: int
    fk_id_venda_extra: Optional[int] = None
    valor_pagamento: Decimal = Field(..., decimal_places=2)
    data_pagamento: Optional[datetime] = None
    data_vencimento: datetime
    metodo_pagamento: Optional[str] = None
    status_pagamento: str
    descricao_pagamento: str

    class Config:
        from_attributes = True
        # Necessário para Pydantic 2.x lidar com Decimal
        json_encoders = {Decimal: lambda v: float(v)}


class PagamentoPayResponse(BaseModel):
    message: str = "Pagamento registrado com sucesso"
    pagamento: PagamentoResponse
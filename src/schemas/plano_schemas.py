from typing import Optional, Annotated
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum

class TipoPlanoEnum(str, Enum):
    mensal = 'mensal'
    trimestral = 'trimestral'
    semestral = 'semestral'
    anual = 'anual'

class ModalidadePlanoEnum(str, Enum):
    one_week = '1x_semana'
    two_week = '2x_semana'
    three_week = '3x_semana'

class PlanoBase(BaseModel):
    tipo_plano: TipoPlanoEnum
    modalidade_plano: ModalidadePlanoEnum
    descricao_plano: Optional[
        Annotated[str, Field(max_length=255)]
    ] = None
    valor_plano: Optional[
        Annotated[
            Decimal, 
            Field(max_digits=10, decimal_places=2)
        ]
    ] = None
    qtde_aulas_totais: int

class PlanoCreate(PlanoBase):
    pass

class PlanoUpdate(BaseModel):
    tipo_plano: Optional[TipoPlanoEnum] = None
    modalidade_plano: Optional[ModalidadePlanoEnum] = None
    descricao_plano: Optional[
        Annotated[str, Field(max_length=255)]
    ] = None
    valor_plano: Optional[
        Annotated[
            Decimal, 
            Field(max_digits=10, decimal_places=2)
        ]
    ] = None
    qtde_aulas_totais: Optional[int] = None

class PlanoInDBBase(PlanoBase):
    id_plano: int

    class Config:
        orm_mode = True

class Plano(PlanoInDBBase):
    pass

from math import erf
import select
from typing import Optional, Annotated
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum

from sqlalchemy import except_

from src.database.connPostGreNeon import CreateSessionPostGre
from src.model.planosModel.planosConfig import Planos

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

def __repr__(self):
    return (
        f"<Planos(id_plano={self.id_plano}, tipo_plano={self.tipo_plano}, "
        f"modalidade_plano={self.modalidade_plano}, valor_plano={self.valor_plano})>"
    )


try:
    db = CreateSessionPostGre()
    session = db.get_session()
    stmt = select(Planos)
    result = session.execute(stmt).unique().all()
    for plano in result:
        print(plano)
    session.close()
except Exception as err:
    print(err)

from pydantic import BaseModel, Field, condecimal
from typing import Optional, List
from enum import Enum
from decimal import Decimal

# --- Enums para a tabela Planos ---

class TipoPlanoEnum(str, Enum):
    MENSAL = 'mensal'
    TRIMESTRAL = 'trimestral'
    SEMESTRAL = 'semestral'
    ANUAL = 'anual'

class ModalidadePlanoEnum(str, Enum):
    UMA_SEMANA = '1x_semana'
    DUAS_SEMANAS = '2x_semana'
    TRES_SEMANAS = '3x_semana'

# --- Schemas de Entrada (Payloads) ---

class PlanoCreate(BaseModel):

    tipo_plano: TipoPlanoEnum
    modalidade_plano: ModalidadePlanoEnum
    descricao_plano: Optional[str] = Field(None, max_length=255)
    
    valor_plano: Decimal = Field(
            ..., 
            max_digits=10, 
            decimal_places=2, 
            gt=Decimal('0.00'), 
            le=Decimal('999.99')
        )    


    qtde_aulas_totais: int = Field(..., gt=0, le=1000)

class PlanoUpdate(BaseModel):
    tipo_plano: Optional[TipoPlanoEnum] = None
    modalidade_plano: Optional[ModalidadePlanoEnum] = None
    descricao_plano: Optional[str] = Field(None, max_length=255)
    
    valor_plano: Optional[Decimal] = Field(
        None, # Padrão é None, indicando que é opcional
        max_digits=10, 
        decimal_places=2, 
        gt=Decimal('0.00'), 
        le=Decimal('999.99')
    )    
    
    qtde_aulas_totais: Optional[int] = Field(None, gt=0, le=1000)

# --- Schemas de Resposta  --
class PlanoResponse(BaseModel):
    id_plano: int
    tipo_plano: TipoPlanoEnum
    modalidade_plano: ModalidadePlanoEnum
    descricao_plano: Optional[str]
    valor_plano: Decimal
    qtde_aulas_totais: int
    
    class Config:
        from_attributes = True
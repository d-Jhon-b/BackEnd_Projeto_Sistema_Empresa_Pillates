from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# --- Schemas de Entrada (Payloads) ---

class PlanoPersonalizadoCreate(BaseModel):
    """Payload para criação de um novo plano personalizado/temporário."""
    nome_plano: str = Field(..., max_length=255)
    tipo_plano_livre: str = Field(..., max_length=100)
    modalidade_plano_livre: str = Field(..., max_length=100)
    descricao_plano: Optional[str] = Field(None, max_length=255)
    
    # Decimal com restrições
    valor_plano: Decimal = Field(
        ..., 
        max_digits=10, 
        decimal_places=2, 
        gt=Decimal('0.00'), 
        le=Decimal('999.99')
    )
    qtde_aulas_totais: int = Field(..., gt=0, le=1000)
    
    is_temporario: bool = False
    data_validade: Optional[datetime] = None 

class PlanoPersonalizadoUpdate(BaseModel):
    """Payload para atualização de um plano personalizado."""
    nome_plano: Optional[str] = Field(None, max_length=255)
    tipo_plano_livre: Optional[str] = Field(None, max_length=100)
    modalidade_plano_livre: Optional[str] = Field(None, max_length=100)
    descricao_plano: Optional[str] = Field(None, max_length=255)
    
    valor_plano: Optional[Decimal] = Field(
        None, 
        max_digits=10, 
        decimal_places=2, 
        gt=Decimal('0.00'), 
        le=Decimal('999.99')
    )
    qtde_aulas_totais: Optional[int] = Field(None, gt=0, le=1000)
    
    is_temporario: Optional[bool] = None
    data_validade: Optional[datetime] = None

# --- Schemas de Resposta (Response) ---

class PlanoPersonalizadoResponse(BaseModel):
    """Schema de resposta para um plano personalizado."""
    id_plano_personalizado: int
    nome_plano: str
    tipo_plano_livre: str
    modalidade_plano_livre: str
    descricao_plano: Optional[str]
    valor_plano: Decimal
    qtde_aulas_totais: int
    is_temporario: bool
    data_criacao: datetime
    data_validade: Optional[datetime]
    
    # class Config:
    #     orm_mode = True # Pydantic V1
    
    class Config:
        from_attributes = True # Pydantic V2
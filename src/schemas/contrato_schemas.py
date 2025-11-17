from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum

# --- Enums ---
class StatusContratoEnum(str, Enum):
    ATIVO = 'ativo'
    SUSPENSO = 'suspenso'
    CANCELADO = 'cancelado'
    EXPIRADO = 'expirado'

class ContratoPlanoFKs(BaseModel):
    fk_id_plano: Optional[int] = Field(default=None, description="ID do Plano Padrão.")
    fk_id_plano_personalizado: Optional[int] = Field(default=None, description="ID do Plano Personalizado.")

    @model_validator(mode='after')
    def check_exactly_one_plano(self) -> 'ContratoPlanoFKs':
        filled_fields = sum(1 for field in [self.fk_id_plano, self.fk_id_plano_personalizado] if field is not None)
        
        if filled_fields == 0:
            raise ValueError("O Contrato deve estar vinculado a um Plano Padrão OU a um Plano Personalizado.")
        
        if filled_fields > 1:
            raise ValueError("Contrato inválido: Não é permitido escolher um Plano Padrão E um Plano Personalizado simultaneamente.")

        return self
    



# --- Schema de Entrada---
class ContratoCreate(BaseModel):
    fk_id_estudante: int = Field(..., description="ID do estudante (deve ser válido).")
    fk_id_adesao_plano: int = Field(..., description="ID da adesão do plano que originou este contrato.")
    
    # Campo que usa a validação de exclusividade
    plano_fks: ContratoPlanoFKs
    
    data_inicio: datetime = Field(..., description="Data de início do contrato.")
    data_termino: datetime = Field(..., description="Data de término do contrato.")
    status_contrato: StatusContratoEnum = Field(default=StatusContratoEnum.ATIVO, description="Status inicial do contrato.")

# --- Schemas de Resposta--
class ContratoResponse(BaseModel):
    id_contrato: int
    #pode ser nulo dado que, caso seja necessário um petição extra judicial para retirada de informações a empresa só terá que aplicar na tabela estudante e usuario, 
    #Dado essa situação a empresa ainda pode vender inforções para obter uma "bonificação" por parte do cliete, caso ele haja de ' má fé"
    fk_id_estudante: Optional[int] 
    fk_id_adesao_plano: Optional[int]
    fk_id_plano: Optional[int]
    fk_id_plano_personalizado: Optional[int]
    data_inicio: datetime
    data_termino: datetime
    status_contrato: StatusContratoEnum
    
    class Config:
        from_attributes = True
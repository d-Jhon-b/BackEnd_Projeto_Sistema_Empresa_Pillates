from pydantic import BaseModel, Field, model_validator
from typing import Optional,Literal
from datetime import datetime, date
from enum import Enum

# --- Enums ---
class StatusContratoEnum(str, Enum):
    ATIVO = 'ativo'
    SUSPENSO = 'suspenso'
    CANCELADO = 'cancelado'
    EXPIRADO = 'expirado'


    
class ContratoCreate(BaseModel):
    fk_id_adesao_plano: int = Field(..., description="ID da adesão de plano que este contrato formaliza.")
    valor_final_negociado: Optional[float] = Field(None, description="Valor final negociado (opcional). Se nulo, usa o valor do plano da Adesão.") 
    
class ContratoResponse(BaseModel):
    id_contrato: int
    fk_id_estudante: Optional[int] = Field(None, description="ID do estudante (preenchido na lógica de busca).") 
    fk_id_adesao_plano: int
    fk_id_plano: Optional[int] = Field(None, description="ID do plano padrão (vindo da Adesão).")
    fk_id_plano_personalizado: Optional[int] = Field(None, description="ID do plano personalizado (vindo da Adesão).")
    data_inicio: datetime
    data_termino: datetime
    aulas_restantes: int
    status_contrato: StatusContratoEnum
    
    class Config:
        from_attributes = True


class ContratoUpdate(BaseModel):
    status_contrato: Optional[Literal['ativo', 'suspenso', 'cancelado', 'expirado']] = Field(
        None, description="Status do contrato (apenas Admin pode alterar)."
    )
    
    data_termino: Optional[date] = Field(None, description="Data de término do contrato.")
    # motivo_cancelamento: Optional[str] = Field(None, max_length=255, description="Descrição do motivo do cancelamento/suspensão.")
    aulas_restantes: Optional[int] = Field(None, description="Ajuste manual do saldo de aulas.")
    class Config:
        from_attributes = True





# class ContratoPlanoFKs(BaseModel):
#     fk_id_plano: Optional[int] = Field(default=None, description="ID do Plano Padrão.")
#     fk_id_plano_personalizado: Optional[int] = Field(default=None, description="ID do Plano Personalizado.")

#     @model_validator(mode='after')
#     def check_exactly_one_plano(self) -> 'ContratoPlanoFKs':
#         filled_fields = sum(1 for field in [self.fk_id_plano, self.fk_id_plano_personalizado] if field is not None)
        
#         if filled_fields == 0:
#             raise ValueError("O Contrato deve estar vinculado a um Plano Padrão OU a um Plano Personalizado.")
        
#         if filled_fields > 1:
#             raise ValueError("Contrato inválido: Não é permitido escolher um Plano Padrão E um Plano Personalizado simultaneamente.")

#         return self
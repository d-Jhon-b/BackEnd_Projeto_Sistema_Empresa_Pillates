from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Any, Callable
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema as cs 

class TypeAdesaoPlano(BaseModel):
    fk_id_plano: Optional[int] = Field(default=None)
    fk_id_plano_personalizado: Optional[int]
    @model_validator(mode='after')
    def aplicar_um_plano(self):
        filled_fields = sum(1 for field in [self.fk_id_plano, self.fk_id_plano_personalizado] if field is not None)
        if filled_fields ==0:
            raise ValueError(f'Você deve fornecer exatamente um: fk_id_plano')
        if filled_fields >1:
            raise ValueError(f'Você deve fornecer exatamente um: fk_id_plano_personalizado')

class SubscribePlanoPayload(BaseModel):
    fk_id_estudante: int
    fk_id_plano_Geral: TypeAdesaoPlano = Field(...)

    
class AdesaoPlanoBase(BaseModel):
    id_adesao_plano: Optional[int] = None
    fk_id_estudante:int
    fk_id_plano:Optional[int] =None
    fk_id_plano_personalizado: Optional[int]=None
    data_adesao: datetime = Field(default_factory=datetime.now)
    data_validade: datetime
    class Config:
        # from_atributes=True
        from_attributes=True 

class SubscribePlano(AdesaoPlanoBase):
    # id_adesao_plano: Optional[int]
    # fk_id_estudante: int  
    # fk_id_plano: int
    pass


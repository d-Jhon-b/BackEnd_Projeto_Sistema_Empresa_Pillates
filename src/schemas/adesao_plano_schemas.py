from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Any, Callable
from datetime import datetime, date
from bson import ObjectId
from pydantic_core import core_schema as cs 

class TypeAdesaoPlano(BaseModel):
    fk_id_plano: Optional[int] = Field(default=None)
    fk_id_plano_personalizado: Optional[int] =Field(default=None)
    @model_validator(mode='after')
    def aplicar_um_plano(self)-> 'TypeAdesaoPlano':
        filled_fields = sum(1 for field in [self.fk_id_plano, self.fk_id_plano_personalizado] if field is not None)
        # if filled_fields == 0:
        #     raise ValueError('Você deve fornecer exatamente um ID de plano (fk_id_plano OU fk_id_plano_personalizado). Nenhum foi fornecido.')
        # if filled_fields > 1:
        #     raise ValueError('Você deve fornecer apenas um ID de plano. Forneça fk_id_plano OU fk_id_plano_personalizado, mas não ambos.')
        if filled_fields != 1:
            raise ValueError('Você deve fornecer exatamente um ID de plano (fk_id_plano OU fk_id_plano_personalizado).')
        return self

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



class AdesaoPlanoUpdate(BaseModel):

    # data_validade: Optional[datetime] = Field(None, description="Nova data de validade da adesão.")
    fk_id_plano: Optional[int] = Field(None, description="Novo ID do plano padrão (Se o plano for alterado).")
    fk_id_plano_personalizado: Optional[int] = Field(None, description="Novo ID do plano personalizado (Se o plano for alterado).")

    class Config:
        extra = 'forbid'
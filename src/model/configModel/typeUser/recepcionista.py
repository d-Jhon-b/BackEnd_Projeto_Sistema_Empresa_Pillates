from pydantic import BaseModel, Field, constr
from typing import Dict, Optional, Union, List
from datetime import date
from enum import Enum


from src.model.configModel.userSettings.valuesUser import NivelAcessoEnum
from src.model.configModel.userConfig import UserConfig

class RecepcionistaConfig(UserConfig):
    """Modelo para Recepcionista (herda de UserConfig)."""
    
    # Assumindo que Recepcionista seja 'colaborador' no seu 'lv_acesso'
    lv_acesso: NivelAcessoEnum = Field(NivelAcessoEnum.COLABORADOR, title='Nível de Acesso', frozen=True)
    
    id_recepcionista: Optional[int] = Field(None, title='ID da Recepcionista', description='ID na tabela recepcionista.')

    
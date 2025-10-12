from pydantic import BaseModel, Field, constr
from typing import Dict, Optional, Union, List
from datetime import date
from enum import Enum

from src.model.configModel.userSettings.valuesUser import NivelAcessoEnum
from src.model.configModel.userConfig import UserConfig


class AdministracaoConfig(UserConfig):
    """Modelo para Administração (herda de UserConfig)."""
    
    # Força o nível de acesso para 'supremo' ou 'colaborador' 
    # Supremo como exemplo para Administracao
    lv_acesso: NivelAcessoEnum = Field(NivelAcessoEnum.SUPREMO, title='Nível de Acesso', frozen=True)
    
    id_adm: Optional[int] = Field(None, title='ID da Administração', description='ID na tabela administracao')


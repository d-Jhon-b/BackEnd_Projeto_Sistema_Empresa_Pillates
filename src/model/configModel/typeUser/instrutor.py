from pydantic import BaseModel, Field, constr
from typing import Dict, Optional, Union, List
from datetime import date
from enum import Enum

from src.model.configModel.userSettings.valuesUser import TipoEspecializacaoProfessorEnum, NivelAcessoEnum
from src.model.configModel.userConfig import UserConfig


class ProfessorConfig(UserConfig):
    """Modelo para Professor (herda de UserConfig)."""
    # Campos específicos da tabela 'professor'
    tipo_especializacao: TipoEspecializacaoProfessorEnum = Field(..., title='Tipo de Especialização', description='CREF ou CREFITA.')
    
    # Força o nível de acesso para 'instrutor' (conforme seu DB 'instrutor')
    lv_acesso: NivelAcessoEnum = Field(NivelAcessoEnum.INSTRUTOR, title='Nível de Acesso', frozen=True)
    
    id_professor: Optional[int] = Field(None, title='ID do Professor', description='ID na tabela professor.')
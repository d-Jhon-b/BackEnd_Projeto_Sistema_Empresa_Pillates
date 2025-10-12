from pydantic import BaseModel, Field, constr
from typing import Dict, Optional, Union, List
from datetime import date
from enum import Enum

from src.model.configModel.userSettings.valuesUser import NivelAcessoEnum
from src.model.configModel.userConfig import UserConfig


class EstudanteConfig(UserConfig):
    """Modelo para Estudante (herda de UserConfig)."""
    # Campos específicos da tabela 'estudante'
    profissao_user: Optional[str] = Field(None, max_length=255, title='Profissão do Usuário (Estudante)')
    historico_medico: str = Field(..., max_length=255, title='Histórico Médico')
    
    # Força o nível de acesso para 'aluno'
    lv_acesso: NivelAcessoEnum = Field(NivelAcessoEnum.ALUNO, title='Nível de Acesso', frozen=True)
    
    # Campo para a chave estrangeira (não é estritamente necessário no Pydantic se o ORM gerencia, 
    # mas ajuda a definir a estrutura do objeto completo, se necessário)
    id_estudante: Optional[int] = Field(None, title='ID do Estudante', description='ID na tabela estudante.')
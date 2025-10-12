from pydantic import Field
from typing import Optional, List

# Importa o modelo base
from src.model.configModel.userConfig import UserConfig 
# Importa o modelo de Endereco (que não estava no base)
from src.model.configModel.userSettings.endereco import Endereco 
# Importa os campos de subtipo para Optional
from src.model.configModel.userSettings.valuesUser import TipoEspecializacaoProfessorEnum

from src.model.configModel.typeUser.adm import AdministracaoConfig
from src.model.configModel.typeUser.alunos import EstudanteConfig
from src.model.configModel.typeUser.instrutor import ProfessorConfig
from src.model.configModel.typeUser.recepcionista import RecepcionistaConfig


class UsuarioCompletoConfig(UserConfig):
    enderecos: Optional[List[Endereco]] = Field(
        None, 
        title='Endereços do Usuário', 
        description='Lista de endereços associados ao usuário.'
    )

    profissao_user: Optional[str] = Field(
        None, 
        max_length=100, 
        title='Profissão do Aluno', 
        description='Apenas se o nível de acesso for ALUNO.'
    )
    historico_medico: Optional[str] = Field(
        None, 
        title='Histórico Médico do Aluno', 
        description='Apenas se o nível de acesso for ALUNO.'
    )

    tipo_especializacao: Optional[TipoEspecializacaoProfessorEnum] = Field(
        None, 
        title='Tipo de Especialização', 
        description='Apenas se o nível de acesso for INSTRUTOR.'
    )

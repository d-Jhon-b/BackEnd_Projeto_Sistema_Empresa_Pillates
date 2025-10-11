from pydantic import BaseModel, Field
from typing import List, Optional

# Importe o modelo base do usuário (os campos da tabela 'usuario')
# **Ajuste este import para o caminho correto da sua UserConfig**
from src.model.userModel.userConfig.userConfig import UserConfig 

# Importe os modelos de detalhes
from src.model.userModel.detailsConfig.enderecoConfig import EnderecoConfig
from src.model.userModel.detailsConfig.contatoConfig import contatoConfig
from src.model.userModel.detailsConfig.emaiConfig import EmailConfig


class UserConfigCompleto(UserConfig):
    """
    Modelo Pydantic para validar a estrutura completa de criação de um usuário,
    incluindo detalhes aninhados.
    """
    # Um usuário pode ter 0 ou mais detalhes. Se precisar de 1 obrigatório, 
    # remova 'default_factory=list'.
    enderecos: List[EnderecoConfig] = Field(default_factory=list, title='Lista de Endereços do Usuário')
    contatos: List[contatoConfig] = Field(default_factory=list, title='Lista de Contatos do Usuário')
    emails: List[EmailConfig] = Field(default_factory=list, title='Lista de Emails do Usuário')
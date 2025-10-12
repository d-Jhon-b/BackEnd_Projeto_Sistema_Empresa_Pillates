from pydantic import BaseModel, Field
from typing import Dict, Optional, Union, List
from datetime import date
from enum import Enum


from src.model.configModel.userSettings.contato import Contato
from src.model.configModel.userSettings.valuesUser import TipoDocumentoEnum, NivelAcessoEnum, TipoEmailEnum



class UserConfig(BaseModel):
    id_user: Optional[int] = Field(None, title='ID do Usuário', description='Identificador único do usuário.')
    name_user: str = Field(..., max_length=100, title='Nome do Usuário') # max_length ajustado para 100
    foto_user: Optional[str] = Field(None, max_length=255, title='Foto do Usuário') # É nullable no DB
    nasc_user: date = Field(..., title='Data de Nascimento do Usuário')
    
    # Usuário (tabela 'usuario')
    tipo_doc_user: TipoDocumentoEnum = Field(..., title='Tipo de Documento', description='CPF ou CNPJ.')
    # num_doc_user: str = Field(..., max_length=14, title='Número do Documento', description='Número do CPF (11 digitos) ou CNPJ (14 digitos).', pattern=r"^\d{11}$|^\d{14}$")
    num_doc_user: str = Field(..., max_length=14, title='Número do Documento', description='Número do CPF (11 digitos) ou CNPJ (14 digitos).')
    lv_acesso: Optional[NivelAcessoEnum] = Field(None, title='Nível de Acesso', description='Supremo, Colaborador, Instrutor ou Aluno.') 
    tipo_email: TipoEmailEnum = Field(..., title='Tipo de E-mail', description='PESSOAL ou COMERCIAL.')
    email_user: str = Field(..., max_length=255, title='E-mail do Usuário') # alterar-update- EmailStr do Pydantic para validação mais estrita futuramente

    #alterar para esconder a senha no banco
    senha_user: str = Field(..., max_length=255, title='Senha do Usuário') # Idealmente, nunca envie a senha em texto puro em um modelo de resposta
    contatos: Optional[List[Contato]] = Field(None, title='Contatos do Usuário', description='Lista de telefones/contatos associados ao usuário.')

  
    
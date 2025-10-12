from pydantic import BaseModel, Field,constr
from typing import Dict, Optional, Union, List
from datetime import date
from enum import Enum


# from model.configModel.userSettings.valuesUser import TipoEnderecoEnum
from .valuesUser import TipoEnderecoEnum


class Endereco(BaseModel):
    """Modelo de validação de dados para Endereço (tabela 'endereco')."""
    id_endereco: Optional[int] = Field(None, title='ID do Endereço')
    tipo_endereco: TipoEnderecoEnum = Field(..., title='Tipo de Endereço')
    endereco: str = Field(..., max_length=255, title='Endereço Completo')
    # constr para garantir que o CEP tenha 8 dígitos #retirado
    cep: str = Field(None, title='CEP') 

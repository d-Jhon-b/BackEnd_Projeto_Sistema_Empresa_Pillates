from pydantic import BaseModel, Field
from typing import Dict, Optional, Union
from datetime import date
from enum import Enum

# from src.model.configModel.userSettings.valuesUser import TipoContatoEnum
from .valuesUser import TipoContatoEnum


REGEX_TELEFONE_BR = r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$" #vc dnv... regex.....

class Contato(BaseModel):
    """Modelo de validação de dados para Contato/Telefone (tabela 'contato')."""
    id_contato: Optional[int] = Field(None, title='ID do Contato', description='Identificador único do contato.')
    
    # Validação do númeor 
    numero_contato: str = Field(
        ..., 
        max_length=255, 
        title='Número do Contato', 
        description='Número de telefone ou celular.',
        pattern=REGEX_TELEFONE_BR # Aplica a validação de formato
    )
    
    tipo_contato: TipoContatoEnum = Field(..., title='Tipo de Contato', description='RESIDENCIAL, COMERCIAL ou FAMILIAR.')

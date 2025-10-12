from enum import Enum
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, constr

# Enums para Tipos de Contato e Acesso
class TipoContatoEnum(str, Enum):
    """Corresponde à coluna 'tipo_contato' na tabela 'contato'."""
    RESIDENCIAL = 'RESIDENCIAL'
    COMERCIAL = 'COMERCIAL'
    FAMILIAR = 'FAMILIAR'

class NivelAcessoEnum(str, Enum):
    """Corresponde à coluna 'lv_acesso' na tabela 'usuario'."""
    SUPREMO = 'supremo'
    COLABORADOR = 'colaborador'
    INSTRUTOR = 'instrutor'
    ALUNO = 'aluno'
    ANONIMO='anonimo'

class TipoDocumentoEnum(str, Enum):
    """Corresponde à coluna 'tipo_doc_user' na tabela 'usuario'."""
    CPF = 'cpf'
    CNPJ = 'cnpj'

class TipoEmailEnum(str, Enum):
    """Corresponde à coluna 'tipo_email' na tabela 'usuario'."""
    PESSOAL = 'pesssoal'
    COMERCIAL = 'comercial'

class TipoEspecializacaoProfessorEnum(str, Enum):
    """Corresponde à coluna 'tipo_especializacao' na tabela 'professor'."""
    CREF = 'cref'
    CREFITA = 'crefita'


class TipoEnderecoEnum(str, Enum):
    """Corresponde à coluna 'tipo_endereco' na tabela 'endereco'."""
    RESIDENCIAL = 'RESIDENCIAL'
    COMERCIAL = 'COMERCIAL'

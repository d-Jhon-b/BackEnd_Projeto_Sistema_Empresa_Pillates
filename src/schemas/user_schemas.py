from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum

# --- Enums que você já criou ---
class TipoContatoEnum(str, Enum):
    RESIDENCIAL = 'residencial'
    COMERCIAL = 'comercial'
    FAMILIAR = 'familiar'

class NivelAcessoEnum(str, Enum):
    SUPREMO = 'supremo'
    COLABORADOR = 'colaborador'
    INSTRUTOR = 'instrutor'
    ALUNO = 'aluno'

class TipoDocumentoEnum(str, Enum):
    CPF = 'cpf'
    CNPJ = 'cnpj'

class TipoEmailEnum(str, Enum):
    PESSOAL = 'pessoal' # Corrigi o typo 'pesssoal'
    COMERCIAL = 'comercial'

class TipoEnderecoEnum(str, Enum):
    RESIDENCIAL = 'residencial'
    COMERCIAL = 'comercial'

# --- Modelos de Dados ---
class EnderecoSchema(BaseModel):
    tipo_endereco: TipoEnderecoEnum
    endereco: str = Field(..., max_length=255)
    cep: Optional[str] = Field(None, max_length=8)

class ContatoSchema(BaseModel):
    tipo_contato: TipoContatoEnum
    numero_contato: str = Field(..., max_length=255)

class ExtraDataAlunoSchema(BaseModel):
    profissao_user: Optional[str] = None
    historico_medico: Optional[str] = None

class UserBaseSchema(BaseModel):
    name_user: str = Field(..., max_length=100)
    nasc_user: Optional[date] = None
    tipo_doc_user: TipoDocumentoEnum
    num_doc_user: str = Field(..., max_length=14)
    lv_acesso: NivelAcessoEnum
    tipo_email: TipoEmailEnum
    email_user: EmailStr # Usar EmailStr do Pydantic para validação automática
    fk_id_estudio: int # O ID do estúdio ao qual o usuário pertence

# --- Payload da Requisição (O que a API vai receber) ---
class UserCreatePayload(BaseModel):
    user_data: UserBaseSchema
    senha_user: str = Field(..., min_length=8)
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    extra_data: Optional[ExtraDataAlunoSchema] = None

# --- Modelo de Resposta (O que a API vai devolver) ---
class UserResponse(UserBaseSchema):
    id_user: int
    class Config:
        orm_mode = True # Permite que o Pydantic leia dados de objetos SQLAlchemy
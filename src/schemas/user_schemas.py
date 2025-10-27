from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum
#---------------------------Enuns paraa uso
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
    PESSOAL = 'pessoal' 
    COMERCIAL = 'comercial'

class TipoEnderecoEnum(str, Enum):
    RESIDENCIAL = 'residencial'
    COMERCIAL = 'comercial'

class TipoEspecializacaoProfessorEnum(str, Enum):
    CREF = 'cref'
    CREFITA = 'crefita'


#Entidades
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
    email_user: EmailStr 
    fk_id_estudio: int 

# class UserCreatePayload(BaseModel):
#     user_data: UserBaseSchema
#     senha_user: str = Field(..., min_length=8)
#     endereco_data: Optional[EnderecoSchema] = None
#     contato_data: Optional[ContatoSchema] = None
#     extra_data: Optional[ExtraDataAlunoSchema] = None


class AlunoCreatePayload(BaseModel):
    user_data: UserBaseSchema
    senha_user: str = Field(..., min_length=8)
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    extra_data: ExtraDataAlunoSchema  

class InstrutorCreatePayload(BaseModel):
    user_data: UserBaseSchema
    senha_user: str = Field(..., min_length=8)
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    tipo_especializacao: TipoEspecializacaoProfessorEnum 
    numero_de_registro:str=Field(..., max_length=50)
    formacao:str=Field(...,max_length=255)
    data_contratacao:date


class ColaboradorCreatePayload(BaseModel):
    user_data: UserBaseSchema
    senha_user: str = Field(..., min_length=8)
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    is_recepcionista: bool = False


#------------Response


class EnderecoResponse(EnderecoSchema):
    id_endereco: int
    class Config:
        from_attributes = True

class ContatoResponse(ContatoSchema):
    id_contato: int
    class Config:
        from_attributes = True

class EstudanteResponse(ExtraDataAlunoSchema):
    id_estudante: int
    class Config:
        from_attributes = True

class ProfessorResponse(BaseModel): 
    id_professor: int 
    tipo_especializacao: TipoEspecializacaoProfessorEnum
    numero_de_registro: str
    formacao: str
    data_contratacao: date
    class Config:
        from_attributes = True

class AdministracaoResponse(BaseModel): 
    id_adm: int
    class Config:
        from_attributes = True

class RecepcionistaResponse(BaseModel): 
    id_recepcionista: int
    class Config:
        from_attributes = True



class UserResponse(UserBaseSchema):
    id_user: int
    lv_acesso: NivelAcessoEnum
    foto_user: Optional[str]
    
    endereco: List[EnderecoResponse] = [] 

    estudante: Optional[EstudanteResponse] = None
    professor: Optional[ProfessorResponse] = None        
    administracao: Optional[AdministracaoResponse] = None
    recepcionista: Optional[RecepcionistaResponse] = None 

    contatos: List[ContatoResponse] = []
    
    class Config:
        from_attributes = True


# -------------- Authentication request schemas XD
class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
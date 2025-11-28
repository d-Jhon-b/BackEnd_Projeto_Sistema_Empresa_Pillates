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
    COLABORADOR = 'colaborador'
    SUPREMO = 'supremo'
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


#-------Schemas para conteudo
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
    fk_id_estudio: Optional[int] = None

# class UserCreatePayload(BaseModel):
#     user_data: UserBaseSchema
#     senha_user: str = Field(..., min_length=8)
#     endereco_data: Optional[EnderecoSchema] = None
#     contato_data: Optional[ContatoSchema] = None
#     extra_data: Optional[ExtraDataAlunoSchema] = None

#--------------Aplicação do conteudo de resposta
class AlunoCreatePayload(BaseModel):
    user_data: UserBaseSchema
    # senha_user: Optional[str] = Field(None, min_length=8)
    senha_user: Optional[str] = None
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    extra_data: ExtraDataAlunoSchema  

class InstrutorCreatePayload(BaseModel):
    user_data: UserBaseSchema
    # senha_user:  Optional[str] = Field(None, min_length=8)
    senha_user: Optional[str] = None #valor opcional para colocar, mas recebe None
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    tipo_especializacao: TipoEspecializacaoProfessorEnum 
    numero_de_registro:str=Field(..., max_length=50)
    formacao:str=Field(...,max_length=255)
    data_contratacao:date


class ColaboradorCreatePayload(BaseModel):
    user_data: UserBaseSchema
    # senha_user:  Optional[str] = Field(None, min_length=8)
    senha_user: Optional[str] = None
    endereco_data: Optional[EnderecoSchema] = None
    contato_data: Optional[ContatoSchema] = None
    is_recepcionista: bool = False


#------------Conteudo de resposta
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

#-----teste
class AlunoResponseName(BaseModel):
    id_user:int
    name_user: str = Field(..., max_length=100)
    nasc_user: Optional[date] = None
    foto_user: Optional[str]

#teste

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
    # fk_id_estudio: int
    
    class Config:
        from_attributes = True


# -------------- Authentication request schemas XD
class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"



#---redefinir senha
class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


#---update 
class EnderecoUpdateSchema(BaseModel):
    id_endereco: Optional[int] = None 
    tipo_endereco: Optional[TipoEnderecoEnum] = None
    endereco: Optional[str] = Field(None, max_length=255)
    cep: Optional[str] = Field(None, max_length=8)

class ContatoUpdateSchema(BaseModel):
    id_contato: Optional[int] = None 
    tipo_contato: Optional[TipoContatoEnum] = None
    numero_contato: Optional[str] = Field(None, max_length=255)

class ExtraDataAlunoUpdateSchema(BaseModel):
    profissao_user: Optional[str] = None
    historico_medico: Optional[str] = None

class ExtraDataInstrutorUpdateSchema(BaseModel):
    tipo_especializacao: Optional[TipoEspecializacaoProfessorEnum] = None
    numero_de_registro: Optional[str] = Field(None, max_length=50)
    formacao: Optional[str] = Field(None, max_length=255)
    data_contratacao: Optional[date] = None

# --- Schemas de Payloads Especializados ---

class AlunoUpdatePayload(BaseModel):
    fk_id_estudio: Optional[int] = None
    name_user: Optional[str] = Field(None, max_length=100)
    email_user: Optional[EmailStr] = None 
    senha_user: Optional[str] = Field(None, min_length=8)

    endereco: Optional[List[EnderecoUpdateSchema]] = None
    contatos: Optional[List[ContatoUpdateSchema]] = None
    
    extra_aluno: Optional[ExtraDataAlunoUpdateSchema] = None

class InstrutorUpdatePayload(BaseModel):
    fk_id_estudio: Optional[int] = None
    name_user: Optional[str] = Field(None, max_length=100)
    email_user: Optional[EmailStr] = None 
    senha_user: Optional[str] = Field(None, min_length=8)

    endereco: Optional[List[EnderecoUpdateSchema]] = None
    contatos: Optional[List[ContatoUpdateSchema]] = None
    
    extra_instrutor: Optional[ExtraDataInstrutorUpdateSchema] = None



class ColaboradorUpdatePayload(BaseModel):
    fk_id_estudio: Optional[int] = None
    name_user: Optional[str] = Field(None, max_length=100)
    email_user: Optional[EmailStr] = None 
    senha_user: Optional[str] = Field(None, min_length=8)

    endereco: Optional[List[EnderecoUpdateSchema]] = None
    contatos: Optional[List[ContatoUpdateSchema]] = None
    
    is_recepcionista: Optional[bool] = None
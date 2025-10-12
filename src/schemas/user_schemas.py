# src/schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from datetime import date

# Importa os Enums do modelo para reutilizá-los na validação
from src.model.userModel import TipoDocUserEnum, NivelAcessoEnum, TipoEmailEnum

# --- Schema Base ---
# Usado para campos que são comuns em várias operações
class UserBase(BaseModel):
    endereco_email: EmailStr # Valida se é um formato de email válido
    name_user: str = Field(..., min_length=3, max_length=100) # Garante que o nome tenha entre 3 e 100 caracteres

# --- Schema para Login ---
# Define exatamente o que é necessário para o endpoint de login
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

# --- Schema para Criar um Usuário ---
# Herda de UserBase e adiciona os outros campos necessários para criar um novo usuário
class UserCreateSchema(UserBase):
    senha_user: str = Field(..., min_length=8) # Senha deve ter no mínimo 8 caracteres
    nasc_user: date
    tipo_doc_user: TipoDocUserEnum
    num_doc_user: str = Field(..., min_length=11, max_length=14)
    lv_acesso: NivelAcessoEnum
    tipo_email: TipoEmailEnum

# --- Schema para Ler/Retornar um Usuário (Resposta da API) ---
# Este schema define quais campos serão enviados de volta para o cliente.
# Note que a senha NÃO está aqui, protegendo dados sensíveis.
class UserSchema(UserBase):
    id_user: int
    lv_acesso: NivelAcessoEnum
    
    class Config:
        # Ajuda o Pydantic a converter o objeto ORM (SQLAlchemy) em um schema
        from_attributes = True
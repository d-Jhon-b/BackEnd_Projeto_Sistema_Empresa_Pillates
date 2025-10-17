from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, CheckConstraint, UniqueConstraint, Date, Enum

class TipoDocumento(Enum):
    CPF = 'cpf'
    CNJP='cnpj'


Base = declarative_base()
class UserModel(Base):
    __tablename__ = 'usuario'
    id_user =Column(Integer, primary_key=True, nullable=True)
    name_user=Column(String(100), nullable=False)
    foto_user=Column(String(255), nullable=False, default='fotoUser.png')
    nasc_user=Column(Date, nullable=True)
    tipo_doc_user=Column(Enum('cpf', 'cnpj', name="tipo_doc_user_enum"), nullable=False)
    num_doc_user = Column(String(14), nullable=False)
    lv_acesso = Column(Enum('supremo', 'colaborador', 'instrutor', 'aluno', name='lv_acesso_enum'), nullable=False)
    tipo_email=Column(Enum('pessoal', 'comercial', name=))
    email_user
    senha_user

, unique=True
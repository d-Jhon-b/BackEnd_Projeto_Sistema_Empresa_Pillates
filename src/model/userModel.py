# src/database/model/user_model.py

import enum
from datetime import date
from typing import Optional

from sqlalchemy import String, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column

# Importa a classe Base do arquivo base.py
from .base import Base

# Criação de Enums em Python para garantir a consistência dos dados
# Isso corresponde aos tipos ENUM que você criou no banco de dados.
class TipoDocUserEnum(str, enum.Enum):
    cpf = "cpf"
    cnpj = "cnpj"

class NivelAcessoEnum(str, enum.Enum):
    supremo = "supremo"
    colaborador = "colaborador"
    instrutor = "instrutor"
    aluno = "aluno"

class TipoEmailEnum(str, enum.Enum):
    pessoal = 'PESSOAL'
    comercial = 'COMERCIAL'


class Usuario(Base):
    """
    Modelo ORM que representa a tabela 'usuario' no banco de dados.
    """
    __tablename__ = "usuario"

    # Mapeamento das colunas da tabela para atributos da classe
    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_user: Mapped[str] = mapped_column(String(100))
    foto_user: Mapped[Optional[str]] = mapped_column(String(255))
    nasc_user: Mapped[date] = mapped_column(Date)
    
    tipo_doc_user: Mapped[TipoDocUserEnum] = mapped_column(Enum(TipoDocUserEnum))
    num_doc_user: Mapped[str] = mapped_column(String(14), unique=True) # unique=True garante que não haja documentos duplicados
    
    lv_acesso: Mapped[NivelAcessoEnum] = mapped_column(Enum(NivelAcessoEnum))
    
    tipo_email: Mapped[TipoEmailEnum] = mapped_column(Enum(TipoEmailEnum))
    endereco_email: Mapped[str] = mapped_column(String(255))
    senha_user: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id_user}, name='{self.name_user}')>"
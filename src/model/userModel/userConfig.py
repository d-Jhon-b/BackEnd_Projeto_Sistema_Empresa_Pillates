from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy import Column, String, Integer, CheckConstraint, UniqueConstraint, Date, Enum, func, ForeignKey

from src.database.Base import DeclarativeBase as Base

from src.model.userModel.valuesUser.enderecoUser import Endereco 
from src.model.userModel.valuesUser.contatoUser import Contato 
from src.model.userModel.typeUser.aluno import Estudante
from src.model.userModel.typeUser.Instrutor import Professor
from src.model.userModel.typeUser.colaborador import Administracao, Recepcionista, Adm_plus



class Usuario(Base.Base):

    __tablename__ = 'usuario'

    id_user =Column(Integer, primary_key=True, nullable=False)
    name_user=Column(String(100), nullable=False)
    foto_user=Column(String(255), nullable=True, default='fotoUser.png')
    nasc_user=Column(Date, nullable=True)
    tipo_doc_user=Column(Enum('cpf', 'cnpj', name="tipo_doc_user_enum"), nullable=False)
    num_doc_user = Column(String(14), nullable=False, unique=True)
    lv_acesso = Column(Enum('supremo', 'colaborador', 'instrutor', 'aluno', name='lv_acesso_enum'), nullable=False)
    tipo_email=Column(Enum('pessoal', 'comercial', name='tipo_email_enum'), nullable=False)
    email_user = Column('email_user',String(255), nullable=False, unique=True)
    senha_user = Column('senha_user', String(255), nullable=False)
    # estudio_aplicado = Column(Enum('itaquera', 'são miguel', name="estudio_aplicado_enum"), nullable=False)
    fk_id_estudio = Column('fk_id_estudio',Integer, ForeignKey('estudio.id_estudio', ondelete='SET NULL'), nullable=True)

    
    
    endereco:Mapped[list["Endereco"]] = relationship(
        back_populates="usuario", 
        uselist=True, # Altere para True se o usuário puder ter vários endereços
        cascade="all, delete-orphan",
    )

    contatos:Mapped[list["Contato"]] = relationship(
        back_populates="usuario", 
        cascade="all, delete-orphan"
    )

    estudante:Mapped[Estudante] = relationship(
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )

    professor:Mapped[Professor] = relationship( 
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    administracao:Mapped[Administracao] = relationship( 
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    recepcionista:Mapped[Recepcionista] = relationship(
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    adm_plus:Mapped[Adm_plus] = relationship(
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )


    def __repr__(self):
        return f"""{self.id_user}\n{self.name_user}\n{self.foto_user}\n{self.nasc_user}\n{self.tipo_doc_user}
        {self.num_doc_user}\n{self.lv_acesso}\n{self.tipo_email}\n{self.email_user}\n{self.senha_user}
        {self.fk_id_estudio}
        """
    



# try:
#     createSession = CreateSessionPostGre()
#     session = createSession.get_session()

#     if not session:
#         print(f'erro ao criar sessão para acesso')
#     else:
        
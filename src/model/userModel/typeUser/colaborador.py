from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre


class Administracao(Base.Base):
    __tablename__ = 'administracao'
    id_adm = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    usuario = relationship(
        "Usuario", 
        back_populates="administracao",
    )

    # def __repr__(self):
    #     return f"<AlunoID(id={self.id_adm}, fk_user_id='{self.fk_id_user}')>"

class Recepcionista(Base.Base):
    __tablename__='recepcionista'
    id_recepcionista = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    usuario = relationship(
        "Usuario", 
        back_populates="recepcionista",
    )

    # def __repr__(self):
    #     return f"<AlunoID(id={self.id_adm}, fk_user_id='{self.fk_id_user}')>"

class Adm_plus(Base.Base):
    __tablename__='adm_plus'
    id_adm_plus = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column('fk_id_user', Integer, ForeignKey('usuario.id_user'), nullable= False)
    usuario = relationship(
        "Usuario", 
        back_populates="adm_plus",
    )

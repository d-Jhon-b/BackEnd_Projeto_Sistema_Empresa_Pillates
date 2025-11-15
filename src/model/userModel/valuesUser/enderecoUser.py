from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import relationship
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre


class Endereco(Base.Base):
    __tablename__ = 'endereco'
    id_endereco = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    tipo_endereco = Column(Enum('residencial', 'comercial', name='tipo_endereco_enum'))
    endereco = Column(String(255), nullable=False)
    cep = Column(String(8), nullable=True)
    usuario = relationship("Usuario", back_populates="endereco")
    def __repr__(self):
        return f"<Endereco(id={self.id_endereco}, tipo='{self.tipo_endereco}', cep='{self.cep}')>"
    


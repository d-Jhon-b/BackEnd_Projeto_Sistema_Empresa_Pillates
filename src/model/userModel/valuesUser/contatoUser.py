from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import relationship
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum


from src.database.Base import DeclarativeBase as Base


from src.database.connPostGreNeon import CreateSessionPostGre

class Contato(Base.Base):
    __tablename__= 'contato'
    id_contato = Column(Integer, primary_key=True, nullable=False)
    fk_id_user =Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    tipo_contato=Column(Enum('residencial', 'comercial', 'familiar', name='tipo_contato_enum'), nullable=False)
    numero_contato = Column(String(255), nullable=False)
    
    usuario = relationship("Usuario", back_populates="contatos")
    def __repr__(self):
        return f'id_contato:{self.id_contato}\ntipoContato:{self.tipo_contato}\nnumero:{self.numero_contato}'
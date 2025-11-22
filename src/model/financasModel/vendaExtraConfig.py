from src.database.Base import DeclarativeBase as Base
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy import Column, Numeric, DateTime,select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from sqlalchemy.ext.associationproxy import association_proxy


# from src.model.financasModel.pagamentoConfig import Pagamento

class VendaExtra(Base.Base):
    __tablename__='venda_extra'

    id_venda_extra = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_estudante = Column(Integer, ForeignKey('estudante.id_estudante', ondelete='SET NULL'), nullable=True)
    
    descricao = Column(String(255), nullable=True)
    valor_venda_extra = Column(Numeric(precision=10, scale=2), nullable=False)
    data_venda = Column(DateTime, nullable=False)

    estudante = relationship("Estudante", back_populates="vendas_extras")
    pagamento= relationship("Pagamento", back_populates="venda_extra", uselist=False) 
    
    def __repr__(self):
        return f"<VendaExtra(id={self.id_venda_extra}, valor={self.valor_venda_extra}, estudante_id={self.fk_id_estudante})>"
from src.database.Base import DeclarativeBase as Base
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy import Column, Numeric, DateTime,select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from sqlalchemy.ext.associationproxy import association_proxy


class Pagamento(Base.Base):

    __tablename__ = 'pagamento' 

    id_pagamento = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    fk_id_contrato = Column(Integer, ForeignKey('contrato.id_contrato'), nullable=False)
    fk_id_estudante = Column(Integer, ForeignKey('estudante.id_estudante'), nullable=False)
    fk_id_venda_extra = Column(Integer, ForeignKey('venda_extra.id_venda_extra'), nullable=True)
    
    valor_pagamento = Column(Numeric(precision=10, scale=2), nullable=False)
    data_pagamento = Column(DateTime, nullable=False)
    data_vencimento = Column(DateTime, nullable=False)
    
    metodo_pagamento = Column(Enum('cartao', 'pix', 'dinheiro', name='enum_metodo_pagamento'), nullable=False)
    status_pagamento = Column(Enum('pago', 'pendente', 'atrasado', name='enum_status_pagamento'), nullable=False)
    descricao_pagamento = Column(String(255), nullable=False)

    contrato = relationship("ContratoConfig", back_populates="pagamentos") 
    estudante = relationship("Estudante", back_populates="pagamentos") 
    venda_extra = relationship("VendaExtra", back_populates="pagamento") # Note: assuming VendaExtra tem relacionamento 1:1 ou 1:N com Pagamento
    
    def __repr__(self):
        return f"<Pagamento(id={self.id_pagamento}, valor={self.valor_pagamento}, status='{self.status_pagamento}')>"
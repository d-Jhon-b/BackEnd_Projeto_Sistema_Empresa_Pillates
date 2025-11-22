from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.model.planosModel.contratoConfig import Contrato


class AdesaoPlano(Base.Base):
    __tablename__ = "adesao_plano"

    id_adesao_plano = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_estudante = Column(Integer, ForeignKey("estudante.id_estudante", ondelete="SET NULL"), nullable=True) 
    fk_id_plano = Column(Integer, ForeignKey('planos.id_plano', ondelete='SET NULL'), nullable=True) 
    fk_id_plano_personalizado = Column(Integer, ForeignKey('planos_personalizados.id_plano_personalizado', ondelete='SET NULL'), nullable=True) 
    data_adesao = Column(DateTime, nullable=False, server_default=func.now()) 
    data_validade = Column(DateTime, nullable=False)

    # estudante = relationship("Estudante", back_populates="adesoes_planos")
    # contratos = relationship("Contrato", back_populates="adesao_plano") 

    # plano = relationship("Planos", back_populates="adesao_planos")

    estudante = relationship("Estudante", back_populates="adesoes_planos")
    contratos = relationship("Contrato", back_populates="adesao_plano") 
    plano_padrao = relationship(
        "Planos", 
        foreign_keys=[fk_id_plano], 
        back_populates="adesao_planos"
    )
    plano_personalizado = relationship(
        "PlanosPersonalizados", 
        foreign_keys=[fk_id_plano_personalizado], 
        back_populates="adesao_planos"
    )
    

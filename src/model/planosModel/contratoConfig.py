from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, func, Enum, CheckConstraint, Numeric
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base
from typing import Optional
# from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
# from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
# from src.model.planosModel.planoConfig import Planos


class Contrato(Base.Base):
    __tablename__ = "contrato"

    id_contrato = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_estudante = Column(Integer, ForeignKey("estudante.id_estudante", ondelete="SET NULL"), nullable=True)
    fk_id_plano = Column(Integer, ForeignKey("planos.id_plano", ondelete="SET NULL"), nullable=True)
    fk_id_plano_personalizado = Column(Integer, ForeignKey("planos_personalizados.id_plano_personalizado", ondelete="SET NULL"), nullable=True)


    fk_id_adesao_plano = Column(Integer, ForeignKey('adesao_plano.id_adesao_plano', ondelete='SET NULL'), nullable=True)

    data_inicio = Column(DateTime, nullable=False)
    data_termino = Column(DateTime, nullable=False) 
    
    valor_final = Column(Numeric(precision=10, scale=2), nullable=False) # <--- Adicionar esta linha!
    aulas_restantes = Column(Integer, nullable=False, default=0)
    status_contrato = Column('status_contrato', Enum('ativo', 'suspenso', 'cancelado', 'expirado', name='enum_status_contrato'), nullable=False)

    __table_args__ = (
        CheckConstraint('fk_id_plano IS NULL OR fk_id_plano_personalizado IS NULL', name='chk_one_plan_fk_active'),
    )
    # estudante = relationship("Estudante", back_populates="contratos") 
    # plano = relationship("Planos", back_populates="contratos")
    # adesao_plano = relationship("AdesaoPlano", back_populates="contratos")
    # plano_personalizado = relationship("PlanosPersonalizados", back_populates="contratos")

    estudante = relationship("Estudante", back_populates="contratos")
    
    plano = relationship("Planos", back_populates="contratos")
    adesao_plano = relationship("AdesaoPlano", back_populates="contratos")
    plano_personalizado = relationship("PlanosPersonalizados", back_populates="contratos")
    pagamentos = relationship(
        'Pagamento', 
        back_populates="contrato",
        cascade="all, delete-orphan"
    )
    


    def __repr__(self):
        return f"id_contrato:{self.id_contrato} | id_estudante:{self.fk_id_estudante} | Status:{self.status_contrato}"    

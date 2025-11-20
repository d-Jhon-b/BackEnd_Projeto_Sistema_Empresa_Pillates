from sqlalchemy import (
    Column, Integer, Numeric, String, CheckConstraint, Enum
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base

# from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
# from src.model.planosModel.contratoConfig import Contrato


class Planos(Base.Base):
    __tablename__ = 'planos' 
    
    id_plano = Column('id_plano', Integer, primary_key=True, autoincrement=True, nullable=False)
    tipo_plano = Column('tipo_plano', Enum('mensal', 'trimestral', 'semestral', 'anual', name='enum_tipo_plano'), nullable=False)
    modalidade_plano = Column('modalidade_plano', Enum('1x_semana', '2x_semana', '3x_semana', name='enum_modalidade_plano'), nullable=False)
    descricao_plano = Column('descricao_plano', String(255), nullable=True)
    valor_plano = Column('valor_plano', Numeric(precision=10, scale=2)) 
    qtde_aulas_totais = Column('qtde_aulas_totais', Integer, nullable=False)
    
    __table_args__ = (
        CheckConstraint('valor_plano <= 999.99', name='chk_valor_plano_max'),
        CheckConstraint('qtde_aulas_totais <= 1000', name='chk_aulas_totais_max')
    )
    
    # adesao_planos = relationship("AdesaoPlano", back_populates="plano")
    # contratos = relationship("Contrato", back_populates="plano")

    adesao_planos = relationship(
        "AdesaoPlano", 
        primaryjoin="Planos.id_plano == AdesaoPlano.fk_id_plano", 
        back_populates="plano_padrao"
    )    
    contratos = relationship("Contrato", back_populates="plano")

    solicitacoes_padrao = relationship(
        "Solicitacoes",
        foreign_keys="[Solicitacoes.fk_id_novo_plano]",
        back_populates="novo_plano_padrao"
    )
    def __repr__(self):
        return f"<Planos(id={self.id_plano}, tipo de plano='{self.tipo_plano}')>"

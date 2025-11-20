from sqlalchemy import (
    Column, Integer, Numeric, String, CheckConstraint, Boolean, DateTime, func
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base




# A classe não precisa dos ENUMs, pois usa String
class PlanosPersonalizados(Base.Base):
    __tablename__ = 'planos_personalizados' 
    
    id_plano_personalizado = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome_plano = Column(String(255), nullable=False)
    tipo_plano_livre = Column(String(100), nullable=False)
    modalidade_plano_livre = Column(String(100), nullable=False)
    descricao_plano = Column(String(255), nullable=True)
    valor_plano = Column(Numeric(precision=10, scale=2), nullable=False) 
    qtde_aulas_totais = Column(Integer, nullable=False)
    is_temporario = Column(Boolean, nullable=False, default=False)
    data_criacao = Column(DateTime, nullable=False, server_default=func.now())
    data_validade = Column(DateTime, nullable=True) 

    __table_args__ = (
        CheckConstraint('valor_plano <= 999.99', name='chk_valor_plano_personalizado_max'),
        CheckConstraint('qtde_aulas_totais <= 1000', name='chk_aulas_totais_personalizado_max')
    )
    
    # Relação de volta para Contrato
    contratos = relationship("Contrato", back_populates="plano_personalizado")
    
    adesao_planos = relationship(
        "AdesaoPlano", 
        # PlanosPersonalizados.id_plano_personalizado deve ser igual a fk_id_plano_personalizado na AdesaoPlano
        primaryjoin="PlanosPersonalizados.id_plano_personalizado == AdesaoPlano.fk_id_plano_personalizado",
        back_populates="plano_personalizado" # O back_populates é o nome que usaremos em AdesaoPlano
    )
    solicitacoes_personalizadas = relationship(
        "Solicitacoes",
        foreign_keys="[Solicitacoes.fk_id_novo_plano_personalizado]",
        back_populates="novo_plano_personalizado"
    )
    def __repr__(self):
        return f"<PlanosPersonalizados(id={self.id_plano_personalizado}, nome='{self.nome_plano}')>"
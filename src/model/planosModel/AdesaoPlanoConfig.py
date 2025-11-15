# src/model/adesaoPlanoModel/AdesaoPlanoConfig.py

from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base


class AdesaoPlanoConfig(Base):
    __tablename__ = "adesao_plano"

    id_adesao_plano = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    fk_id_user = Column(Integer, ForeignKey("usuario.id_user", ondelete="CASCADE"), nullable=False)

    # NOVO — ligação direta com plano
    fk_id_plano = Column(Integer, ForeignKey("planos.id_plano", ondelete="CASCADE"), nullable=False)

    data_adesao = Column(DateTime, nullable=False, server_default=func.now())
    data_validade = Column(DateTime, nullable=False)

    # relacionamentos
    usuario = relationship("UsuarioConfig", back_populates="adesoes_planos")
    plano = relationship("Planos", back_populates="adesoes_usuarios")

    def to_dict(self):
        return {
            "id_adesao_plano": self.id_adesao_plano,
            "fk_id_user": self.fk_id_user,
            "fk_id_plano": self.fk_id_plano,
            "data_adesao": self.data_adesao.isoformat(),
            "data_validade": self.data_validade.isoformat(),
        }

# src/model/adesaoPlanoModel/adesaoPlanoConfig.py
from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base


class AdesaoPlanoConfig(Base):
    __tablename__ = "adesao_plano"

    id_adesao_plano = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey("usuario.id_user", ondelete="CASCADE"), nullable=False)
    data_adesao = Column(DateTime, nullable=False, server_default=func.now())
    data_validade = Column(DateTime, nullable=False)

    # Relacionamento para acessar o usuário da adesão
    usuario = relationship("UsuarioConfig", back_populates="adesoes_planos")


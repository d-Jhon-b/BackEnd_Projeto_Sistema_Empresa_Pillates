from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Numeric, Column, String, Integer,select, CheckConstraint, UniqueConstraint, Date, Enum, func, ForeignKey
from src.database.Base import DeclarativeBase as Base
from src.database.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.database.connPostGreNeon import CreateSessionPostGre

class AdesaoPlanoConfig(Base):
    __tablename__ = "adesao_plano"

    id_adesao_plano = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey("usuario.id_user", ondelete="CASCADE"), nullable=False)
    data_adesao = Column(DateTime, nullable=False)
    data_validade = Column(DateTime, nullable=False)

    # Relacionamento para acessar o usuário da adesão
    usuario = relationship("UsuarioConfig", back_populates="adesoes_planos")

# Exemplo de relacionamento inverso em UsuarioConfig (deve ter)
# class UsuarioConfig(Base):
#     __tablename__ = "usuario"
#     ...
#     adesoes_planos = relationship("AdesaoPlanoConfig", back_populates="usuario")

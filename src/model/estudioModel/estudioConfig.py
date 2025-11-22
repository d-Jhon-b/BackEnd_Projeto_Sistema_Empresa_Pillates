from sqlalchemy import Column, String, Integer
from src.database.Base import DeclarativeBase as Base
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import select,Column, String, Integer, CheckConstraint, UniqueConstraint, Date, Enum, func, ForeignKey
from src.database.connPostGreNeon import CreateSessionPostGre


class Estudio(Base.Base):
    __tablename__ = 'estudio'

    id_estudio = Column(Integer, primary_key=True, nullable=False)
    endereco_estudio = Column(String(255), nullable=False, unique=True)
    cep_estudio = Column(String(8), nullable=False)
    mongo_registros_estudio = Column(String(255), nullable=False)
    solicitacoes = relationship("Solicitacoes", back_populates="estudio")
    def __repr__(self):
        return f"<Estudio(id={self.id_estudio}, endereco='{self.endereco_estudio}')>"
    
from datetime import datetime
from typing import List, Any

from sqlalchemy import create_engine, Column, Integer, DateTime, String
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient

SQLALCHEMY_DATABASE_URL = "postgresql://usuario:senha@localhost:5432/seubanco"
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
Base = declarative_base()

class AgendamentoSQL(Base):
    __tablename__ = "agendamento"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aulaId = Column(Integer, nullable=False)
    alunoId = Column(Integer, nullable=False)
    dataHoraAgendada = Column(DateTime, nullable=False)
    status = Column(String(50), default="Agendado")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
mongo_client = MongoClient(MONGODB_CONNECTION_STRING)
mongo_db = mongo_client['pilates_db']

class AgendamentoModel:
    @staticmethod
    def agendar_sql(aula_id: int, aluno_id: int, data_hora: datetime, status: str = "Agendado") -> int:
        db = SessionLocal()
        agend = AgendamentoSQL(
            aulaId=aula_id,
            alunoId=aluno_id,
            dataHoraAgendada=data_hora,
            status=status
        )
        db.add(agend)
        db.commit()
        db.refresh(agend)
        db.close()
        return agend.id

    @staticmethod
    def agendar_mongo(aula_id: int, aluno_id: int, data_hora: datetime, status: str = "Agendado") -> Any:
        doc = {
            "aulaId": aula_id,
            "alunoId": aluno_id,
            "dataHoraAgendada": data_hora,
            "status": status
        }
        result = mongo_db.agendamentos.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def consultar_sql(aluno_id: int) -> List[AgendamentoSQL]:
        db = SessionLocal()
        agendamentos = db.query(AgendamentoSQL).filter(AgendamentoSQL.alunoId == aluno_id).all()
        db.close()
        return agendamentos

    @staticmethod
    def consultar_mongo(aluno_id: int) -> list:
        return list(mongo_db.agendamentos.find({"alunoId": aluno_id}))


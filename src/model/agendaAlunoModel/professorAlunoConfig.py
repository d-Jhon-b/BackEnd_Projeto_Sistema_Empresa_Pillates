from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from src.database.Base import DeclarativeBase as Base

class ProfessorEstudante(Base):
    __tablename__ = 'professor_estudante'
    
    fk_id_estudante = Column(Integer, ForeignKey('estudante.id_estudante'), nullable=False, primary_key=True)
    fk_id_professor = Column(Integer, ForeignKey('professor.id_professor'), nullable=False, primary_key=True)
    
    __table_args__ = (
        PrimaryKeyConstraint('fk_id_estudante', 'fk_id_professor'),
    )
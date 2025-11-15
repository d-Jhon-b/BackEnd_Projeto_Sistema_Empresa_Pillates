from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base
# Importar Estudante e Professor
from src.model.userModel.typeUser.Instrutor import Professor
from src.model.userModel.typeUser.aluno import Estudante


class RegistroDoAluno(Base):
    __tablename__ = 'registro_do_aluno'
    
    id_resgitro = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_estudante = Column(Integer, ForeignKey('estudante.id_estudante'), nullable=False)
    fk_id_professor = Column(Integer, ForeignKey('professor.id_professor'), nullable=False)
    mongo_arquivo_id = Column(String(255), nullable=False)
    
    # Relacionamentos (Relationships)
    estudante = relationship("Estudante", back_populates="registros") 
    professor = relationship("Professor", back_populates="registros") 
    
    def __repr__(self):
        return f"<Registro(id={self.id_resgitro}, estudante_id={self.fk_id_estudante})>"
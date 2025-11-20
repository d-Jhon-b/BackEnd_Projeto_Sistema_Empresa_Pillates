from sqlalchemy.orm import Query, Mapped, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import (select, insert, DefaultClause, Integer, Date, 
DateTime, Column, String,Enum, ForeignKey, CheckConstraint)

# from src.model.userModel.typeUser.aluno import Estudante
from sqlalchemy.ext.associationproxy import association_proxy
from src.database.Base import DeclarativeBase as Base

class Aula(Base.Base):
    __tablename__ = 'aula'
    id_aula = Column('id_aula', Integer, primary_key=True, autoincrement=True, nullable=False)
    data_aula=Column('data_aula', DateTime, nullable=False)
    titulo_aula=Column('titulo_aula',String(255), nullable=False)
    desc_aula=Column('desc_aula',String(255), nullable=True, default=f"Aula de {titulo_aula}")
    fk_id_estudio=Column('fk_id_estudio', Integer, ForeignKey('estudio.id_estudio'), nullable=False)
    fk_id_professor=Column('fk_id_professor', Integer, ForeignKey('professor.id_professor'), nullable=False)
    fk_id_professor_substituto=Column('fk_id_professor_substituto', Integer, ForeignKey('professor.id_professor'), nullable=True)
    __table_args__=(
    CheckConstraint('fk_id_professor != fk_id_professor_substituto', name='chk_titular_substituto_diferentes'),
    )



    estudantes_associacao: Mapped[list["Estudante_Aula"]] = relationship(
        "Estudante_Aula",
        back_populates="aula", 
        cascade="all, delete-orphan"
    )
    solicitacao_aula_sugerida = relationship('Solicitacoes', back_populates='aula_referencia')
    estudantes = association_proxy("estudantes_associacao", "estudante")
    def __repr__(self):
        return f'\nid:{self.id_aula}\ndata da aula:{self.data_aula}\ntitulo da aula:{self.titulo_aula}\n'



class Estudante_Aula(Base.Base):
    __tablename__='estudante_aula'
    fk_id_estudante=Column('fk_id_estudante', Integer, ForeignKey('estudante.id_estudante'), nullable=False, primary_key=True)
    fk_id_aula=Column('fk_id_aula', Integer, ForeignKey('aula.id_aula'), nullable=False, primary_key=True)    
    tipo_de_aula=Column('tipo_de_aula', Enum('normal', 'experimental', 'reposicao', name="enum_tipo_de_aula"), nullable=False)
    
    estudante = relationship( 
        'Estudante', 
        back_populates='aulas_associacao', 
        uselist=False 
    )
    
    aula = relationship(
        'Aula',
        back_populates='estudantes_associacao', 
        uselist=False
    )

    def __repr__(self):
        return f'\nid do estudante cadastrado:{self.fk_id_estudante}\nid da aula{self.fk_id_aula}\n tipo da aula:{self.tipo_de_aula} '

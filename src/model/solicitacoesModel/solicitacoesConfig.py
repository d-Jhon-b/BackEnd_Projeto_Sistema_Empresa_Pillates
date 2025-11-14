from sqlalchemy import Integer, String,Text, DateTime,ForeignKey, Column, Enum, text,UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from src.database.Base import DeclarativeBase as Base   
from src.model.estudioModel.estudioConfig import Estudio 

class Solicitacoes(Base.Base):
    __tablename__ ='solicitacoes'

    id_solicitacao = Column('id_solicitacao', Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_user = Column('fk_id_user',Integer, ForeignKey('usuario.id_user'), nullable=True)
    fk_id_estudio = Column('fk_id_estudio',Integer, ForeignKey('estudio.id_estudio'), nullable=False)
    tipo_de_solicitacao = Column('tipo_de_solicitacao', Enum('aula','plano','pagamento', 'outros', name='enum_solcitacao'), nullable=False)
    menssagem=Column('menssagem', Text, nullable=True)
    status_solicitacao=Column('status_solicitacao', Enum('atendida', 'recusada','em espera', name='enum_status_solicitacao'),nullable=False, default="em espera")
    data_criacao=Column('data_criacao',DateTime,nullable=False, server_default=text('now()'))
    data_resposta=Column('data_resposta', DateTime, nullable=True)

    # usuario=relationship(
    #     "Usuario",
    #     back_populates="solicitacoes"
    # )
    

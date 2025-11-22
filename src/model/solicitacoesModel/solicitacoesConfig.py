from sqlalchemy import Integer, String,Text, DateTime,ForeignKey, Column, Enum, text,UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, Mapped

from src.database.Base import DeclarativeBase as Base   
from src.model.estudioModel.estudioConfig import Estudio 



class Solicitacoes(Base.Base):
    __tablename__ ='solicitacoes'

    id_solicitacao = Column('id_solicitacao', Integer, primary_key=True, autoincrement=True, nullable=False)
    # fk_id_user = Column('fk_id_user',Integer, ForeignKey('usuario.id_user'), nullable=True)
    fk_id_estudante = Column('fk_id_estudante',Integer, ForeignKey('estudante.id_estudante'), nullable=True)
    fk_id_estudio = Column('fk_id_estudio',Integer, ForeignKey('estudio.id_estudio'), nullable=False)
    tipo_de_solicitacao = Column('tipo_de_solicitacao', Enum('aula','plano','pagamento', 'outros', name='enum_solcitacao'), nullable=False)
    menssagem=Column('menssagem', Text, nullable=True)
    status_solicitacao=Column('status_solicitacao', Enum('atendida', 'recusada','em espera', name='enum_status_solicitacao'),nullable=False, server_default="em espera")
    data_criacao=Column('data_criacao',DateTime,nullable=False, server_default=text('now()'))
    data_resposta=Column('data_resposta', DateTime, nullable=True)

    acao_solicitacao_aula = Column(
        'acao_solicitacao_aula', 
        Enum('AGENDAMENTO', 'REAGENDAMENTO', 'CANCELAMENTO', name='enum_acao_solicitacao_aula'), 
        nullable=True
    )

    acao_solicitacao_plano = Column(
        'acao_solicitacao_plano', 
        Enum('MUDANCA_PLANO', 'CANCELAMENTO_PLANO', 'RENOVACAO_PLANO', name='enum_acao_solicitacao_plano'), 
        nullable=True
    )
    fk_id_aula_referencia = Column(Integer, ForeignKey('aula.id_aula'), 
        nullable=True,
        comment="ID da aula que está sendo referenciada (para reagendamento/cancelamento)"
    )
    data_sugerida = Column(DateTime, nullable=True)
    fk_id_novo_plano = Column(Integer, ForeignKey('planos.id_plano'), nullable=True)
    fk_id_novo_plano_personalizado = Column(Integer, ForeignKey('planos_personalizados.id_plano_personalizado'), nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            '(fk_id_novo_plano IS NULL) OR (fk_id_novo_plano_personalizado IS NULL)', 
            name='chk_one_new_plan_fk_active'
        ),
    )
    estudante = relationship("Estudante", back_populates="solicitacoes")
    estudio = relationship("Estudio", back_populates="solicitacoes")

    aula_referencia = relationship('Aula', back_populates='solicitacao_aula_sugerida')

    novo_plano_padrao = relationship(
        "Planos", 
        foreign_keys=[fk_id_novo_plano],
        back_populates="solicitacoes_padrao"
    )
    novo_plano_personalizado = relationship(
        "PlanosPersonalizados", 
        foreign_keys=[fk_id_novo_plano_personalizado],
        back_populates="solicitacoes_personalizadas"
    )


    def __repr__(self):
        # Ajustado para usar o fk_id_estudante
        return f"""
        id:{self.id_solicitacao}\nestudio_id:{self.fk_id_estudio}\nestudante_id:{self.fk_id_estudante}\nmenssagem:{self.menssagem}\nstatus:{self.status_solicitacao}
        """
    

    # usuario=relationship(
    #     "Usuario",
    #     back_populates="solicitacoes"
    # )

    # def __repr__(self):
    #     return f"""
    #     id:{self.id_solicitacao}\nestudio_id:{self.fk_id_estudio}\nuser_id:{self.fk_id_user}\nmenssagem:{self.menssagem}\nstatus:{self.status_solicitacao}
    #     """
    

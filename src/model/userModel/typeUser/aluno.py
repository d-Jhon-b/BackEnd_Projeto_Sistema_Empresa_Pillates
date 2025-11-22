from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from sqlalchemy.ext.associationproxy import association_proxy

from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre
from src.model.aulaModel.aulaConfig import Estudante_Aula

from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.contratoConfig import Contrato

from src.model.financasModel.pagamentoConfig import Pagamento
from src.model.financasModel.vendaExtraConfig import VendaExtra

class Estudante(Base.Base):
    __tablename__ = 'estudante'
    id_estudante = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    profissao_user = Column(String(255), nullable=True)
    historico_medico = Column(String(255), nullable=False)
    usuario = relationship(
        "Usuario", 
        back_populates="estudante",
    )

    aulas_associacao: Mapped[list["Estudante_Aula"]] = relationship(
        "Estudante_Aula",
        back_populates="estudante", 
        cascade="all, delete-orphan",
    )
    
    aulas = association_proxy("aulas_associacao", "aula")

    contratos= relationship(
        "Contrato",
        back_populates="estudante",
        cascade="all, delete-orphan",
    )
    
    adesoes_planos= relationship(
        "AdesaoPlano",
        back_populates="estudante",
        cascade="all, delete-orphan",
    )
    
    pagamentos: Mapped[list["Pagamento"]] = relationship(
        "Pagamento",
        back_populates="estudante",
        cascade="all, delete-orphan", # Ajuste o cascade conforme sua regra de negócio, mas 'delete-orphan' é comum
    )
    vendas_extras: Mapped[list["VendaExtra"]] = relationship(
        "VendaExtra",
        back_populates="estudante",
        cascade="all, delete-orphan", 
    )
    solicitacoes = relationship(
        'Solicitacoes',
        back_populates="estudante",
        cascade='all, delete-orphan'
    )

    
    def __repr__(self):
        return f"<AlunoID(id={self.id_estudante}, fk_user_id='{self.fk_id_user}\nprofissão:{self.profissao_user}\nhistorico:{self.historico_medico}')>"
    

# if __name__ == "__main__":
#     try:
#         createSession = CreateSessionPostGre()
#         session = createSession.get_session()

#         comand = select(Estudante)
#         res = session.execute(comand)
#         todos_res = res.scalars().all()
#         print(todos_res)
#     except Exception as err:
#         print(err)
#     finally:
#         session.close()
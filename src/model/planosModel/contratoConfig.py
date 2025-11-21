from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, func, Enum, CheckConstraint, Numeric
)
from sqlalchemy.orm import relationship
from src.database.Base import DeclarativeBase as Base
from typing import Optional
# from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
# from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
# from src.model.planosModel.planoConfig import Planos


class Contrato(Base.Base):
    __tablename__ = "contrato"

    id_contrato = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fk_id_estudante = Column(Integer, ForeignKey("estudante.id_estudante", ondelete="SET NULL"), nullable=True)
    fk_id_plano = Column(Integer, ForeignKey("planos.id_plano", ondelete="SET NULL"), nullable=True)
    fk_id_plano_personalizado = Column(Integer, ForeignKey("planos_personalizados.id_plano_personalizado", ondelete="SET NULL"), nullable=True)


    fk_id_adesao_plano = Column(Integer, ForeignKey('adesao_plano.id_adesao_plano', ondelete='SET NULL'), nullable=True)

    data_inicio = Column(DateTime, nullable=False)
    data_termino = Column(DateTime, nullable=False) 
    
    valor_final = Column(Numeric(precision=10, scale=2), nullable=False) # <--- Adicionar esta linha!
    aulas_restantes = Column(Integer, nullable=False, default=0)
    status_contrato = Column('status_contrato', Enum('ativo', 'suspenso', 'cancelado', 'expirado', name='enum_status_contrato'), nullable=False)

    __table_args__ = (
        CheckConstraint('fk_id_plano IS NULL OR fk_id_plano_personalizado IS NULL', name='chk_one_plan_fk_active'),
    )
    # estudante = relationship("Estudante", back_populates="contratos") 
    # plano = relationship("Planos", back_populates="contratos")
    # adesao_plano = relationship("AdesaoPlano", back_populates="contratos")
    # plano_personalizado = relationship("PlanosPersonalizados", back_populates="contratos")

    estudante = relationship("Estudante", back_populates="contratos")
    
    plano = relationship("Planos", back_populates="contratos")
    adesao_plano = relationship("AdesaoPlano", back_populates="contratos")
    plano_personalizado = relationship("PlanosPersonalizados", back_populates="contratos")
    pagamentos = relationship(
        'Pagamento', 
        back_populates="contrato",
        cascade="all, delete-orphan"
    )
    


    def __repr__(self):
        return f"id_contrato:{self.id_contrato} | id_estudante:{self.fk_id_estudante} | Status:{self.status_contrato}"    





#-------parte do roberto:


# def to_dict(self) -> Dict[str, Any]:
#     return {
#         "id_contrato": self.id_contrato,
#         "fk_id_user": self.fk_id_user,
#         "fk_id_plano": self.fk_id_plano,
#         "data_inicio": self.data_inicio.isoformat() if self.data_inicio else None,
#         "data_fim": self.data_fim.isoformat() if self.data_fim else None,
#         "valor": float(self.valor) if self.valor is not None else None,
#         "moeda": self.moeda,
#         "status": self.status,
#     }


# # ======= CRUD helper =======
# class ContratoModel:
#     @staticmethod
#     def criar_contrato(dados: Dict[str, Any]) -> ContratoConfig:
#         """Cria um novo contrato.

#         dados: dicionário contendo as chaves compatíveis com ContratoConfig.
#         Exemplo: {"fk_id_user": 1, "fk_id_plano": 2, "valor": 49.90, "data_fim": datetime(...)}
#         """
#         session = CreateSessionPostGre()
#         try:
#             # normalizar campos numéricos / datas, se necessário
#             if "valor" in dados:
#                 # evitar problemas com Decimal
#                 dados["valor"] = Decimal(str(dados["valor"]))

#             novo = ContratoConfig(**dados)
#             session.add(novo)
#             session.commit()
#             session.refresh(novo)
#             return novo
#         except SQLAlchemyError as e:
#             session.rollback()
#             raise
#         finally:
#             session.close()

#     @staticmethod
#     def buscar_por_id(contrato_id: int) -> Optional[ContratoConfig]:
#         session = CreateSessionPostGre()
#         try:
#             return session.query(ContratoConfig).filter(ContratoConfig.id_contrato == contrato_id).one_or_none()
#         finally:
#             session.close()

#     @staticmethod
#     def buscar_por_usuario(user_id: int) -> List[ContratoConfig]:
#         session = CreateSessionPostGre()
#         try:
#             return session.query(ContratoConfig).filter(ContratoConfig.fk_id_user == user_id).all()
#         finally:
#             session.close()

#     @staticmethod
#     def atualizar_status(contrato_id: int, novo_status: ContratoStatus) -> Optional[ContratoConfig]:
#         session = CreateSessionPostGre()
#         try:
#             contrato = session.query(ContratoConfig).filter(ContratoConfig.id_contrato == contrato_id).one_or_none()
#             if contrato is None:
#                 return None
#             contrato.status = novo_status.value
#             session.add(contrato)
#             session.commit()
#             session.refresh(contrato)
#             return contrato
#         except SQLAlchemyError:
#             session.rollback()
#             raise
#         finally:
#             session.close()

#     @staticmethod
#     def atualizar_campos(contrato_id: int, campos: Dict[str, Any]) -> Optional[ContratoConfig]:
#         """Atualiza campos permitidos do contrato."""
#         session = CreateSessionPostGre()
#         try:
#             contrato = session.query(ContratoConfig).filter(ContratoConfig.id_contrato == contrato_id).one_or_none()
#             if contrato is None:
#                 return None

#             # campos permitidos — evitar sobrescrever chaves sensíveis
#             permitidos = {"fk_id_plano", "data_fim", "valor", "moeda"}
#             for k, v in campos.items():
#                 if k in permitidos:
#                     if k == "valor":
#                         v = Decimal(str(v))
#                     setattr(contrato, k, v)

#             session.add(contrato)
#             session.commit()
#             session.refresh(contrato)
#             return contrato
#         except SQLAlchemyError:
#             session.rollback()
#             raise
#         finally:
#             session.close()

#     @staticmethod
#     def deletar_contrato(contrato_id: int) -> bool:
#         session = CreateSessionPostGre()
#         try:
#             contrato = session.query(ContratoConfig).filter(ContratoConfig.id_contrato == contrato_id).one_or_none()
#             if contrato is None:
#                 return False
#             session.delete(contrato)
#             session.commit()
#             return True
#         except SQLAlchemyError:
#             session.rollback()
#             raise
#         finally:
#             session.close()


# # ======= Exemplo de relacionamento inverso esperado =======
# # No modelo UsuarioConfig:
# # contratos = relationship("ContratoConfig", back_populates="usuario", cascade="all, delete")
# #
# # No modelo Planos (planosConfig):
# # contratos = relationship("ContratoConfig", back_populates="plano")


# # ======= Exemplo de uso (não executar em import) =======
# if __name__ == "__main__":
#     # exemplo rápido — apenas para testes locais
#     sample = {
#         "fk_id_user": 1,
#         "fk_id_plano": None,
#         "valor": 29.9,
#         "moeda": "BRL",
#     }

#     c = ContratoModel.criar_contrato(sample)
#     print("Contrato criado:", c.to_dict())

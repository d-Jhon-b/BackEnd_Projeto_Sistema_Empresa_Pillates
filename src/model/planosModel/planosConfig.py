from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Numeric, Column, String, Integer,select, CheckConstraint, UniqueConstraint, Date, Enum, func, ForeignKey
from fastapi import Depends
from src.database.Base import DeclarativeBase as Base
from src.database.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.database.connPostGreNeon import CreateSessionPostGre


class Planos(Base.Base):
    __tablename__ = 'planos'
    id_plano = Column('id_plano',Integer, primary_key=True, autoincrement=True, nullable=False)
    tipo_plano = Column(Enum('mensal', 'trimestral', 'semestral', 'anual', name='enum_tipo_plano'), nullable=False)
    modalidade_plano = Column(Enum('1x_semana', '2x_semana', '3x_semana', name='enum_modalidade_plano'), nullable=False)
    descricao_plano = Column(String(255), nullable=True)
    valor_plano=Column(Numeric(precision=10, scale=2))
    qtde_aulas_totais =Column(Integer, nullable=False)


    #não podemos aplicar as constrains como atributos soltos na tabela
    #usar o __table_args__ referencia que são argumentos "adicionais" da tabela
    __table_args__=(

    CheckConstraint('valor_plano <= 999.99', name='chk_valor_plano_max'),
    CheckConstraint('qtde_aulas_totais <= 1000',name='chk_aulas_totais_max')

    )

    def __repr__(self):
        return f"<Estudio(id={self.id_plano}, tipo de plano='{self.tipo_plano}')>"


# if __name__ == "__main__":
#     create_session = CreateSessionPostGre()
#     db = create_session.get_session()
#     # db:Session = Depends(get_db())
#     try:
#         stmt = select(Planos)

#         print("Executando a query no banco de dados Neon...")
#         result = db.execute(stmt)
#         todos_planos = result.scalars().all()
#         for planos in todos_planos:
#             print(planos)
#     except SQLAlchemyError as err:
#         print(err)
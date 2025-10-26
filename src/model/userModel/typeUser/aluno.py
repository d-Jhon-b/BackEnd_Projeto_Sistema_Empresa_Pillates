from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
# from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre


class Estudante(Base.Base):
    __tablename__ = 'estudante'
    id_estudante = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    profissao_user = Column(String(255), nullable=True)
    historico_medico = Column(String(255), nullable=False)

    # def __repr__(self):
    #     return f"<AlunoID(id={self.id_estudante}, fk_user_id='{self.fk_id_user}\nprofissão:{self.profissao_user}\nhistorico:{self.historico_medico}')>"
    

# if __name__ == "__main__":
#     try:
#         createSession = CreateSessionPostGre()
#         session = createSession.get_session()

#         if not session:
#             print(f'erro ao criar sessão para acesso')
#         else:

#             comand = select(Estudante)
#             res = session.execute(comand)
#             todos_res = res.scalars().all()
#             print(todos_res)
#     except Exception as err:
#         print(err)
#     finally:
#         session.close()
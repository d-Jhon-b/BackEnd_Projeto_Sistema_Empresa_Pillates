from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
# from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre


class Administracao(Base.Base):
    __tablename__ = 'administracao'
    id_adm = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)


    # def __repr__(self):
    #     return f"<AlunoID(id={self.id_adm}, fk_user_id='{self.fk_id_user}')>"

class Recepcionista(Base.Base):
    __tablename__='recepcionista'
    id_recepcionista = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)

    # def __repr__(self):
    #     return f"<AlunoID(id={self.id_adm}, fk_user_id='{self.fk_id_user}')>"


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
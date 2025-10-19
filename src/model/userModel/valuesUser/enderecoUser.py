from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
# from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre


class Endereco(Base.Base):
    __tablename__ = 'endereco'
    id_endereco = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    tipo_endereco = Column(Enum('RESIDENCIAL', 'COMERCIAL', name='tipo_endereco_enum'))
    endereco = Column(String(255), nullable=False)
    cep = Column(String(8), nullable=True)

    def __repr__(self):
        return f"<Endereco(id={self.id_endereco}, tipo='{self.tipo_endereco}', cep='{self.cep}')>"
    

# if __name__ == "__main__":
#     try:
#         createSession = CreateSessionPostGre()
#         session = createSession.get_session()

#         if not session:
#             print(f'erro ao criar sessão para acesso')
#         else:

#             comand = select(Endereco)
#             res = session.execute(comand)
#             todos_res = res.scalars().all()
#             print(todos_res)
#     except Exception as err:
#         print(err)
#     finally:
#         session.close()
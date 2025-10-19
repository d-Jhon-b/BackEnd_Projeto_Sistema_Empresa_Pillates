from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
# from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base

from src.database.connPostGreNeon import CreateSessionPostGre


class Professor(Base.Base):
    __tablename__ = 'professor'
    id_professor = Column(Integer, primary_key=True, nullable=False)
    fk_id_user = Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    tipo_especializacao = Column(Enum('cref', 'crefita', name='tipo_especializacao_enum'), nullable=False)
    numero_de_registro= Column(String(50), nullable=False)
    formacao=Column(String(255), nullable=True)
    data_contratacao=Column(Date, nullable=False)

    def __repr__(self):
        return f"\n\n\n<Professor(id={self.id_professor},\n\nformação:{self.formacao}\n\nfk_user_id='{self.fk_id_user}\n\n\ntipo_especializacao:{self.tipo_especializacao}'\n\n\n data de contratação:{self.data_contratacao})>"
    

# if __name__ == "__main__":
#     try:
#         createSession = CreateSessionPostGre()
#         session = createSession.get_session()

#         if not session:
#             print(f'erro ao criar sessão para acesso')
#         else:
#             comand = select(Professor)
#             res = session.execute(comand)
#             todos_res = res.scalars().all()
#             print(todos_res)
#     except Exception as err:
#         print(err)
#     finally:
#         session.close()
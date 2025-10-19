from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
# from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, select,ForeignKey,String, Integer, CheckConstraint, UniqueConstraint, Date, Enum
from src.database.Base import DeclarativeBase as Base


from src.database.connPostGreNeon import CreateSessionPostGre

class Contato(Base.Base):
    __tablename__= 'contato'
    id_contato = Column(Integer, primary_key=True, nullable=False)
    fk_id_user =Column(Integer, ForeignKey('usuario.id_user'), nullable= False)
    tipo_contato=Column(Enum('RESIDENCIAL', 'COMERCIAL', 'FAMILIAR', name='tipo_contato_enum'), nullable=False)
    numero_contato = Column(String(255), nullable=False)
    def __repr__(self):
        return f'id_contato:{self.id_contato}\ntipoContato:{self.tipo_contato}\nnumero:{self.numero_contato}'
    

# if __name__ == "__main__":
#     try:
#         create_session = CreateSessionPostGre()
#         session = create_session.get_session()
#         if not session:
#             print(f'erro ao criar sessão')
#         else:
#             comand = select(Contato)
#             res = session.execute(comand)
#             todos_res = res.scalars().all()
#             print(todos_res)
#     except Exception as err:
#         print(f'{err}')
#     finally:
#         session.close()
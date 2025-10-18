from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Union
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, CheckConstraint, UniqueConstraint, Date, Enum, func, ForeignKey

from src.database.Base import DeclarativeBase as Base


class Usuario(Base.Base):

    __tablename__ = 'usuario'

    id_user =Column(Integer, primary_key=True, nullable=False)
    name_user=Column(String(100), nullable=False)
    foto_user=Column(String(255), nullable=True, default='fotoUser.png')
    nasc_user=Column(Date, nullable=True)
    tipo_doc_user=Column(Enum('cpf', 'cnpj', name="tipo_doc_user_enum"), nullable=False)
    num_doc_user = Column(String(14), nullable=False, unique=True)
    lv_acesso = Column(Enum('supremo', 'colaborador', 'instrutor', 'aluno', name='lv_acesso_enum'), nullable=False)
    tipo_email=Column(Enum('pessoal', 'comercial', name='tipo_email_enum'), nullable=False)
    email_user = Column('email_user',String(255), nullable=False, unique=True)
    senha_user = Column('senha_user', String(255), nullable=False)
    estudio_aplicado = Column(Enum('itaquera', 'são miguel', name="estudio_aplicado_enum"), nullable=False)
    fk_id_estudio = Column('fk_id_estudio',Integer, ForeignKey('estudio.id_estudio'), nullable=False)


    # estudio = relationship("Estudio", back_populates="usuarios")

    def __repr__(self):
        return f"<UsuarioModel(id={self.id_user}, name='{self.name_user}', email='{self.email_user}')>"
    
    
# if __name__ == "__main__":
    
#     # Importações necessárias apenas para o teste
#     from sqlalchemy import select  # <<< IMPORTAÇÃO CRUCIAL
#     from src.database.connPostGreNeon import CreateSessionPostGre
#     db_session_creator = CreateSessionPostGre()
#     session = db_session_creator.get_session()

#     if not session:
#         print(" Falha ao obter sessão. Verifique a conexão com o banco.")
#     else:
#         try:
#             # A LINHA QUE CORRIGE O ERRO: `select()` cria a instrução correta.
#             stmt = select(UsuarioModel)
            
#             print("Executando a query no banco de dados Neon...")
#             result = session.execute(stmt)
#             todos_os_usuarios = result.scalars().all()

#             if not todos_os_usuarios:
#                 print("\n SUCESSO: A consulta funcionou, mas nenhum usuário foi encontrado.")
#                 print("   Este é o resultado esperado, pois o banco de dados está vazio.")
#             else:
#                 print(f"\n SUCESSO: Consulta bem-sucedida! {len(todos_os_usuarios)} usuário(s) encontrado(s):")
#                 for user in todos_os_usuarios:
#                     print(f"  -> {user}")

#         except Exception as e:
#             print(f" Ocorreu um erro durante a consulta: {e}")
#         finally:
#             session.close()
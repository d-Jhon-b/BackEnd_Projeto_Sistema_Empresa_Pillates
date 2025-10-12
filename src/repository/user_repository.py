# src/repository/user_repository.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Importa o modelo ORM
from src.model.userModel import Usuario

class UserRepository:
    """
    Camada de acesso a dados para a entidade Usuário.
    Contém todas as operações de banco de dados relacionadas a usuários.
    """
    def __init__(self, db_session: AsyncSession):
        # A sessão do banco de dados é injetada para que possamos usá-la
        self.db_session = db_session

    async def get_user_by_email(self, email: str) -> Optional[Usuario]:
        """
        Busca um único usuário no banco de dados pelo seu endereço de e-mail.

        Args:
            email: O e-mail do usuário a ser buscado.

        Returns:
            Um objeto do tipo Usuario se encontrado, caso contrário, None.
        """
        # Cria a query para selecionar o usuário onde o e-mail corresponde
        query = select(Usuario).where(Usuario.endereco_email == email)
        
        # Executa a query de forma assíncrona
        result = await self.db_session.execute(query)
        
        # Retorna o primeiro resultado encontrado (ou None)
        return result.scalars().first()
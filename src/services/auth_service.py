from typing import Optional

from src.model.userModel import Usuario
from src.repository.user_repository import UserRepository
# Importa a função de verificação do novo local
from src.core.security import verify_password

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> Optional[Usuario]:
        user = await self.user_repository.get_user_by_email(email)

        if not user or not verify_password(password, user.senha_user):
            return None

        return user


# # src/services/auth_service.py

# from typing import Optional
# from passlib.context import CryptContext

# # Importa o modelo e o repositório
# from src.model.userModel import Usuario
# from src.repository.user_repository import UserRepository

# # Cria um contexto para o hashing de senhas, especificando o algoritmo bcrypt
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class AuthService:
#     """
#     Camada de serviço para a lógica de negócio de autenticação.
#     """
#     def __init__(self, user_repository: UserRepository):
#         # Injeta o repositório de usuário para acessar o banco de dados
#         self.user_repository = user_repository

#     def verify_password(self, plain_password: str, hashed_password: str) -> bool:
#         """Verifica se a senha em texto plano corresponde à senha criptografada."""
#         return pwd_context.verify(plain_password, hashed_password)

#     async def authenticate_user(self, email: str, password: str) -> Optional[Usuario]:
#         """
#         Autentica um usuário.

#         1. Busca o usuário pelo e-mail usando o repositório.
#         2. Se o usuário existir, verifica se a senha fornecida está correta.

#         Returns:
#             O objeto Usuario se a autenticação for bem-sucedida, caso contrário, None.
#         """
#         # Pede ao repositório para buscar o usuário no banco
#         user = await self.user_repository.get_user_by_email(email)

#         # Se não encontrou um usuário com esse e-mail ou a senha não bate, a autenticação falha.
#         if not user or not self.verify_password(password, user.senha_user):
#             return None

#         # Se tudo estiver correto, retorna o objeto do usuário
#         return user
from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod

# Importe sua classe de inserção
from src.model.userModel.operationsDB.insertModel import InsertValues

# 1. CLASSE BASE ABSTRATA (Define o "contrato")
class BaseUserType(ABC):
    """
    Define a interface comum para todos os tipos de comportamento de usuário.
    """
    def __init__(self, user_data):
        self.user_data = user_data

    @abstractmethod
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Optional[Union[int, bool]]:
        """Método para inserir dados. A implementação varia por tipo de usuário."""
        pass

# 2. COMPORTAMENTO DO ALUNO (Não tem permissão para inserir)
class AlunoUser(BaseUserType):
    """
    Implementação para usuários do tipo 'aluno'.
    Não possui permissões de escrita no banco.
    """
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> None:
        print(f"🚫 AÇÃO NEGADA: Usuários do tipo 'aluno' não podem inserir dados.")
        # Lançar um erro é uma opção ainda melhor para a lógica da aplicação
        # raise PermissionError("Usuários do tipo 'aluno' não têm permissão para inserir dados.")
        return None

# 3. COMPORTAMENTO DO ADMINISTRADOR (Pode inserir dados)
class AdminUser(BaseUserType):
    """
    Implementação para usuários com permissões de administrador.
    Contém a lógica para interagir com o banco de dados.
    """
    def __init__(self, user_data):
        super().__init__(user_data)
        # O administrador ganha a "ferramenta" de inserção
        self.db_inserter = InsertValues()
        print("🔧 Ferramenta de inserção inicializada para o Admin.")

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Optional[Union[int, bool]]:
        print(f"🔑 Admin executando inserção na tabela '{table_name}'...")
        try:
            # Delega a chamada para a classe InsertValues
            return self.db_inserter.insert(table_name, **data)
        except Exception as e:
            print(f"Erro durante a operação de inserção do admin: {e}")
            return None

# 4. COMPORTAMENTO DO ADMIN SUPREMO (Herda do Admin)
class SupremoUser(AdminUser):
    """
    Implementação para o super administrador. Herda todas as capacidades
    do Admin e pode ter funcionalidades adicionais no futuro.
    """
    def __init__(self, user_data):
        super().__init__(user_data)
        # Pode ter ferramentas adicionais no futuro
        print("👑 SupremoUser inicializado com todas as permissões de Admin.")
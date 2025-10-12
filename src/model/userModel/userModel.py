from pydantic import BaseModel, Field, BeforeValidator, ConfigDict, ValidationError, model_validator
from typing import Union, Optional, Any, Annotated, Dict
from enum import Enum
from bson import ObjectId
from datetime import date


from src.model.userModel.userConfig.userConfig import UserConfig, LevelAccess
from src.model.userModel.user_types import BaseUserType, AlunoUser, AdminUser, SupremoUser
# from src.model.userModel.operationsDB.insertModel import InsertValues



class UserModel():
    #def __init__(self, tipoUser:str, data:Dict[str,Any]):
    USER_ROLE_MAP = {
        'aluno': AlunoUser,
        'instrutor': AlunoUser, # Instrutor também não insere dados (exemplo)
        'colaborador': AdminUser,
        'supremo': SupremoUser,
    }


#    def __init__(self, tipoUser:str, data:Dict[str,Any]):
    def __init__(self,  data:Dict[str,Any]):
        
        # self.tipoUser = tipoUser
        self.config: Optional[UserConfig] = None 
        self.db_inserter = InsertValues()
        # self.role_behavior: Optional[BaseUserType] = None # <-- ESTA LINHA FOI ADICIONADA

        try:
            self.config = UserConfig(**data)
            print("Dados do usuário validados e carregados com sucesso!")

            # user_level = self.config.lv_acesso.value # Pega o valor do Enum (ex: 'aluno')
            # # Busca a classe correta no nosso mapa
            # BehaviorClass = self.USER_ROLE_MAP.get(user_level)
            
            # if BehaviorClass:
            #     # 3. CRIE e INJETE o comportamento no modelo
            #     self.role_behavior = BehaviorClass(self.config)
            #     print(f"-> Comportamento '{BehaviorClass.__name__}' atribuído ao usuário.")
            # else:
            #     raise ValueError(f"Nível de acesso '{user_level}' não é válido ou não tem um comportamento definido.")

        except (ValidationError, ValueError) as err:
            print(f"❌ Erro ao criar modelo de usuário: {err}")
            # Relança o erro para que o código que chamou saiba da falha
            raise err
        



    def save_to_database(self) -> Optional[int]:
        """
        Orquestra a inserção de um novo usuário e seus dados relacionados
        em múltiplas tabelas de forma transacional.
        """
        if not self.config:
            print("Erro: Não é possível salvar um usuário não validado.")
            return None

        print("🚀 Iniciando processo de gravação no banco de dados...")
        
        # 1. Preparar os dados para a tabela 'usuario'
        user_table_data = self.config.model_dump(
            exclude={'details', 'profissao_user', 'historico_medico', 'senha_user'}
        )
        # Adicione o hash da senha aqui!
        # user_table_data['senha_user'] = hash_function(self.config.senha_user)

        try:
            # 2. Inserir na tabela principal 'usuario' e obter o ID
            print("   - Inserindo dados na tabela 'usuario'...")
            user_id = self.db_inserter.insert('usuario', **user_table_data)
            
            if not user_id:
                raise Exception("Falha ao obter o ID do usuário após a inserção.")
            
            print(f"   - Usuário base criado com ID: {user_id}")

            # 3. Inserir dados nas tabelas de detalhes (contato, endereco)
            for contato in self.config.details.contatos:
                contato_data = contato.model_dump()
                contato_data['fk_id_user'] = user_id
                self.db_inserter.insert('contato', **contato_data)
            print(f"   - {len(self.config.details.contatos)} contato(s) inserido(s).")
            
            for endereco in self.config.details.enderecos:
                endereco_data = endereco.model_dump()
                endereco_data['fk_id_user'] = user_id
                self.db_inserter.insert('endereco', **endereco_data)
            print(f"   - {len(self.config.details.enderecos)} endereço(s) inserido(s).")

            # 4. Inserir dados na tabela de papel específica (A LÓGICA PRINCIPAL)
            user_level = self.config.lv_acesso
            if user_level == LevelAccess.ALUNO:
                print("   - Inserindo dados na tabela 'estudante'...")
                estudante_data = {
                    'fk_id_user': user_id,
                    'profissao_user': self.config.profissao_user,
                    'historico_medico': self.config.historico_medico
                }
                self.db_inserter.insert('estudante', **estudante_data)

            elif user_level == LevelAccess.COLABORADOR:
                print("   - Inserindo dados na tabela 'administracao'...")
                admin_data = {'fk_id_user': user_id}
                self.db_inserter.insert('administracao', **admin_data)

            elif user_level == LevelAccess.SUPREMO:
                print("   - Inserindo dados nas tabelas 'administracao' e 'adm_plus'...")
                admin_data = {'fk_id_user': user_id}
                self.db_inserter.insert('administracao', **admin_data)
                self.db_inserter.insert('adm_plus', **admin_data)

            print("✅ Processo de gravação concluído com sucesso!")
            return user_id

        except Exception as e:
            print(f"🔥 ERRO CRÍTICO DURANTE A GRAVAÇÃO: {e}. A transação será revertida.")
            # A lógica de rollback já está dentro do seu InsertValues, o que é ótimo!
            return None
    # def insert_data(self, table_name: str, data: Dict[str, Any]) -> Optional[Union[int, bool]]:
    #     """
    #     Delega a operação de inserção para o objeto de comportamento.
    #     """
    #     if self.role_behavior:
    #         return self.role_behavior.insert_data(table_name, data)
    #     else:
    #         print("Erro: Usuário não foi inicializado com um comportamento válido.")
    #         return None

    # def get_data_for_database(self) -> Dict[str, Any]:
    #     """Retorna os dados validados, prontos para o banco."""
    #     if self.config:
    #         # Excluindo a senha e os detalhes que serão inseridos separadamente
    #         return self.config.model_dump(exclude={'senha_user', 'details'})
    #     return {}













dados_admin_supremo = {
    "name_user": "Super Admin",
    "nasc_user": "1990-01-01",
    "tipo_doc_user": "cnpj",
    "num_doc_user": "11222333000181",
    "lv_acesso": "supremo", # <-- NÍVEL DE ACESSO
    "tipo_email_user": "COMERCIAL",
    "email_user": "supremo@empresa.com",
    "senha_user": "SuperSenhaAdmin123!",
    # Adicionando um contato para testar a inserção de detalhes
    "contatos": [
        {"tipo_contato": "COMERCIAL", "numero_contato": "1133334444"}
    ]
}

# --- Dados para um usuário Aluno (com os campos obrigatórios) ---
dados_aluno_completo = {
    "name_user": "Aluno Dedicado",
    "nasc_user": "2005-05-05",
    "tipo_doc_user": "cpf",
    "num_doc_user": "55566677788",
    "lv_acesso": "aluno", # <-- NÍVEL DE ACESSO
    "tipo_email_user": "PESSOAL",
    "email_user": "aluno.dedicado@escola.com",
    "senha_user": "SenhaAluno456",
    
    # Campos específicos e OBRIGATÓRIOS para o papel 'aluno'
    "profissao_user": "Estudante de TI",
    "historico_medico": "Nenhuma condição pré-existente.",

    # Adicionando um endereço para testar a inserção de detalhes
    "enderecos": [
        {"tipo_endereco": "RESIDENCIAL", "endereco": "Rua dos Livros, 42", "cep": "87654321"}
    ]
}


print("--- 1. TESTANDO CRIAÇÃO DO USUÁRIO SUPREMO ---")
try:
    # Passo 1: Validar os dados e criar o modelo em memória
    admin_user = UserModel(data=dados_admin_supremo)
    
    # Passo 2: Chamar o método para salvar tudo no banco de dados
    novo_id = admin_user.save_to_database()

    if novo_id:
        print(f"\n🎉 Sucesso! Usuário SUPREMO criado com o ID: {novo_id}")
    else:
        print("\n😔 Falha ao criar o usuário SUPREMO no banco de dados.")

except (ValidationError, ValueError) as e:
    print(f"\n🔥 Erro no processo de criação do usuário SUPREMO: {e}")


print("\n" + "="*50 + "\n")


print("--- 2. TESTANDO CRIAÇÃO DO USUÁRIO ALUNO ---")
try:
    # Passo 1: Validar os dados e criar o modelo em memória
    aluno_user = UserModel(data=dados_aluno_completo)
    
    # Passo 2: Chamar o método para salvar tudo no banco de dados
    novo_id = aluno_user.save_to_database()

    if novo_id:
        print(f"\n🎉 Sucesso! Usuário ALUNO criado com o ID: {novo_id}")
    else:
        print("\n😔 Falha ao criar o usuário ALUNO no banco de dados.")

except (ValidationError, ValueError) as e:
    print(f"\n🔥 Erro no processo de criação do usuário ALUNO: {e}")

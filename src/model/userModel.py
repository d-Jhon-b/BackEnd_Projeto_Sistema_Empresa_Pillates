from typing import Dict, Any, Optional, List
import bcrypt # Para hashing de senha
import json # Para tratamento de dados
import logging


# from src.model.configModel.userConfig import UserConfig # O esquema base
# from src.model.configModel.typeUser.adm import AdministracaoConfig # Exemplo de esquema de subtipo

from src.model.configModel.all_user_config import UsuarioCompletoConfig # Seu schema que engloba tudo, se existir

from src.model.configModel.operations.insertModel import InserValues # Sua classe de INSERT
from src.model.configModel.operations.selectModel import SelectValues # Sua classe de SELECT


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class UserModel:
    def __init__(self, tipoUser: str):

        self.user_executor_type = tipoUser.lower()
        self.inserter = InserValues(self.user_executor_type)
        self.selector = SelectValues() # 
        
        if not self.inserter.pode_inserir:
            logging.warning("AVISO: UserModel inicializado, mas sem permissão/conexão para inserções.")


    
    def inserir_novo_usuario(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # try:
        #     self.usuario_validado = UsuarioCompletoConfig(**user_data) 
        # except Exception as e:
        #     return {'status': 'error', 'message': f'Erro de validação de dados: {e}'}

        # self.senha_plana = self.usuario_validado.senha_user
        self.user_data = user_data
        self.senha_plana = user_data.get('senha_user')
        if not self.senha_plana:
            # Se por algum motivo a senha não estiver no dict (o que não deve acontecer), falha
            return {'status': 'error', 'message': 'Campo senha_user ausente nos dados validados.'}
        
        self.hashed_password_bytes = bcrypt.hashpw(
            self.senha_plana.encode('utf-8'), 
            bcrypt.gensalt()
        )
        # self.usuario_validado.senha_user = self.hashed_password_bytes.decode('utf-8')
        # self.dados_para_insercao = self.usuario_validado.model_dump()
        # self.resultado_db = self.inserter.inserirNovoUsuario(self.dados_para_insercao)
        # return self.resultado_db
        

        self.user_data['senha_user'] = self.hashed_password_bytes.decode('utf-8')
        self.resultado_db = self.inserter.inserirNovoUsuario(user_data)
        return self.resultado_db


    def fazer_login(self, email: str, senha_plana: str) -> Optional[Dict[str, Any]]:     
        dados_usuario = self.selector.selecionar_por_email(email)
        
        if not dados_usuario:
            logging.warning(f"Tentativa de login falhou: Usuário {email} não encontrado.")
            return None # Usuário não encontrado
            
        hash_armazenado = dados_usuario['senha_user'].strip().encode('utf-8')
        
        # 2. Verificar a senha (bcrypt)
        if bcrypt.checkpw(senha_plana.encode('utf-8'), hash_armazenado):
            logging.info(f"Login bem-sucedido para o usuário ID: {dados_usuario['id_user']}.")
            
            # Remove o hash da senha antes de retornar os dados do usuário para a Controller
            dados_usuario.pop('senha_user', None) 
            return dados_usuario 
        else:
            logging.warning(f"Tentativa de login falhou: Senha incorreta para {email}.")
            return None
    
    # def buscar_usuario_por_id(self, user_id: int) -> Optional[Dict[str, Any]]:

    #     return self.selector.get_user_base_info(user_id)



# class MockInserValues:
#     def __init__(self, tipoUser: str):
#         self.pode_inserir = True
#     def inserirNovoUsuario(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
#         return {'status': 'success', 'message': 'Usuário inserido (MOCK)'}

# # Mock para SelectValues (simula a leitura do DB)
# class MockSelectValues:
#     # Dados do seu usuário de teste, incluindo o HASH
#     MOCK_USER_DATA = {
#         'id_user': 10,
#         'nome': 'Jhoni',
#         'lv_acesso': 'supremo',
#         'email': 'teste@gmail.com',
#         'senha_user': '$2b$12$uFvMRIb/eCCtsJD3e2nPwuEhmtiSDaZhkXVsp286V8j.ky9tlUgg2' 
#     }
    
#     def selecionar_por_email(self, email: str) -> Optional[Dict[str, Any]]:
#         # Simula a busca: se o email for o de teste, retorna os dados com o hash
#         if email == "teste@gmail.com":
#             return self.MOCK_USER_DATA.copy()
#         # Simula erro de usuário não encontrado
#         return None

# if __name__ == "__main__":
    
#     print("-" * 50)
#     print("EXECUTANDO TESTE DE LOGIN ISOLADO PARA UserModel")
#     print("-" * 50)

#     # Substitui as classes reais pelas mocks no escopo do teste
#     InserValues = MockInserValues
#     SelectValues = MockSelectValues
    
#     TEST_EMAIL_OK = "teste@gmail.com"
#     TEST_PASSWORD_OK = "962266514"
#     TEST_PASSWORD_FAIL = "senhaerrada"
    
#     user_model_test = UserModel("aluno") 
    
#     user_data_success = user_model_test.fazer_login(TEST_EMAIL_OK, TEST_PASSWORD_OK)
    
#     if user_data_success:
#         print(" Resultado do Login OK:")
#         print(json.dumps(user_data_success, indent=4))
#     else:
#         print(" FALHA no Teste de Sucesso! A verificação de senha falhou.")

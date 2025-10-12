from src.database.envConfig.getEnv import EnvLoader
from typing import Optional, Dict, List

class EnvLoaderJwt(EnvLoader):

    def __init__(self):

        super().__init__("api.env")
        
    def get_config(self) -> Dict[str, Optional[str]]:
        self._load()
        keys_to_load: List[str] = [
            "JWT_SECRET_KEY", 
            "JWT_ALGORITHM", 
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
        ]
        config_data = self._get_all(keys_to_load)
        
        expire_key = "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
        expire_minutes = config_data.get(expire_key)
        
        if expire_minutes is not None:
             try:
                 config_data[expire_key] = int(expire_minutes)
             except ValueError:
                 raise ValueError(f"A variável '{expire_key}' deve ser um número inteiro, mas o valor '{expire_minutes}' foi encontrado.")
        
        for key in keys_to_load:
            if config_data.get(key) is None:
                raise ValueError(f"A variável '{key}' é obrigatória e não foi encontrada.")
        
        return config_data
    


# if __name__ == "__main__":
#     print("-" * 50)
#     print("INICIANDO TESTE ISOLADO DE EnvLoaderJwt")
#     try:
#         # Tenta instanciar e obter a configuração
#         loader_jwt = EnvLoaderJwt()
#         config = loader_jwt.get_config()
        
#         print("Configurações JWT carregadas com sucesso:")
#         for key, value in config.items():
#             # Exibe a chave de forma segura
#             if key == "JWT_SECRET_KEY" and isinstance(value, str):
#                 print(f"- {key}: {value[:5]}...{value[-5:]} (mascarado)")
#             else:
#                 print(f"- {key}: {value} (Tipo: {type(value).__name__})")
        
#         # Confirma que a conversão para INT ocorreu
#         assert isinstance(config.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"), int)
        
#         print("\nSUCESSO: Carregamento do .env e conversão de tipos confirmados.")

#     except FileNotFoundError as e:
#         print(f"ERRO: Arquivo .env não encontrado. Verifique se 'config/api.env' existe.")
#     except Exception as e:
#         print(f"ERRO DURANTE O TESTE: {e}")
#     finally:
#         print("-" * 50)

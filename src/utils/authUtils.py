from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
# 1. Importa HTTPBearer e HTTPAuthorizationCredentials em vez de OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from src.database.envConfig.envJwt import EnvLoaderJwt 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bearer_scheme = HTTPBearer(scheme_name="Bearer (JWT Personalizado)")



class JWTAuthManager:
    """
    Gerencia todas as operações de JWT
    """
    def __init__(self):
        # Carregamento de Configurações JWT do .env
        try:
            jwt_config = EnvLoaderJwt().get_config()
        except Exception as e:
            logging.error(f"Falha ao carregar configurações JWT do .env: {e}")
            raise RuntimeError(f"A API não pode iniciar sem as configurações JWT corretas: {e}")

        # Atribui as constantes como atributos da classe
        self.secret_key = jwt_config["JWT_SECRET_KEY"]
        self.algorithm = jwt_config["JWT_ALGORITHM"]
        self.expire_minutes = jwt_config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]


    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        
        # Define o tempo de expiração
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        
        to_encode.update({"exp": expire})
        
        # Codifica com os atributos da classe
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            # Decodifica com os atributos da classe
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None


    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
        token = credentials.credentials 
        payload = self.decode_access_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload

# Instância global do gerenciador de autenticação para ser usada em toda a aplicação.
auth_manager = JWTAuthManager()

#   #teste de obtemção do jwt_v1 XD
# if __name__ == "__main__":
#     print("-" * 50)
    
#     try:
#         #Dados de usuário fictício
#         test_user_data = {
#             "id_user": 999,
#             "lv_acesso": "SUPREMO"
#         }

#         #  Criar o token
#         test_token = auth_manager.create_access_token(test_user_data)
#         print(f"Token criado (mascarado): {test_token[:15]}...{test_token[-15:]}")

#         decoded_payload = auth_manager.decode_access_token(test_token)
        
#         if decoded_payload and decoded_payload.get("id_user") == test_user_data["id_user"]:
#             print("\nSUCESSO: Token criado e decodificado com sucesso!")
#             # Tenta decodificar um token inválido (apenas para teste de erro)
#             print("\nTestando token inválido...")
#             if auth_manager.decode_access_token(test_token + "INVALIDO") is None:
#                  print("SUCESSO: Token inválido rejeitado corretamente.")
#             else:
#                  print("FALHA: Token inválido aceito!")
#         else:
#             print("FALHA: O payload decodificado não corresponde aos dados originais.")

#     except RuntimeError as e:
#         print(f"\nERRO FATAL: Falha ao inicializar o gerenciador (configuração do .env). Detalhes: {e}")
#     except Exception as e:
#         print(f"\nERRO DESCONHECIDO DURANTE O TESTE: {e}")
#     finally:
#         raise



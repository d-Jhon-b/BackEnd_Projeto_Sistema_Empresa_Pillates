from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from src.database.envConfig.envJwt import EnvLoaderJwt 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bearer_scheme = HTTPBearer(scheme_name="Bearer (JWT Personalizado)")

class JWTAuthManager:
    """
    Gerencia todas as operações de JWT, incluindo carregamento de 
    configurações, criação de tokens, decodificação/validação, e serve 
    como dependência do FastAPI via o método __call__.
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
        """Gera um token JWT com base nos dados do usuário."""
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
        """Decodifica e valida o token JWT."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None


    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
        """ Recebe as credenciais HTTP (esquema e token) via HTTPBearer."""
        token = credentials.credentials 
        
        payload = self.decode_access_token(token)

        # print(f'\n\n[authUtils] Payload decodificado: {payload}\n\n')
        # print(f'\n\n[authUtils] Payload decodificado: {payload}\n\n')

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload

# Instância global do gerenciador de autenticação para ser usada em toda a aplicação.
auth_manager = JWTAuthManager()

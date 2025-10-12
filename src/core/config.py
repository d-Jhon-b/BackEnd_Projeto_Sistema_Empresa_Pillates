# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # As variáveis que devem ser lidas do arquivo .env
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

# Cria uma instância global das configurações
settings = Settings()
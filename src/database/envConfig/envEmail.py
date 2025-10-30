# src/database/envConfig/envEmail.py
from src.database.envConfig.getEnv import EnvLoader
from typing import List
from fastapi_mail import ConnectionConfig
import logging

class EnvLoaderEmail(EnvLoader):

    def __init__(self):
        super().__init__("api.env")
        
    def get_config(self) -> ConnectionConfig:
        self._load()
        keys_to_load: List[str] = [
            "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM",
            "MAIL_PORT", "MAIL_SERVER", "MAIL_STARTTLS", "MAIL_SSL_TLS"
        ]
        config_data = self._get_all(keys_to_load)

        for key in keys_to_load:
            if config_data.get(key) is None:
                raise ValueError(f"A variável de e-mail '{key}' é obrigatória.")

        try:
            return ConnectionConfig(
                MAIL_USERNAME=config_data.get("MAIL_USERNAME"),
                MAIL_PASSWORD=config_data.get("MAIL_PASSWORD"),
                MAIL_FROM=config_data.get("MAIL_FROM"),
                MAIL_PORT=int(config_data.get("MAIL_PORT")),
                MAIL_SERVER=config_data.get("MAIL_SERVER"),
                MAIL_STARTTLS=config_data.get("MAIL_STARTTLS").lower() in ('true', '1'),
                MAIL_SSL_TLS=config_data.get("MAIL_SSL_TLS").lower() in ('true', '1'),
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Variáveis de e-mail inválidas: {e}")
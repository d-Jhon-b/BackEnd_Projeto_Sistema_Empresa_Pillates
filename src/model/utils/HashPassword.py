import bcrypt # Para hashing de senha
import json # Para tratamento de dados
import logging
class HashPassword():
    @staticmethod
    def hash_password(password_user):
        password_user_hash = bcrypt.hashpw(
            password_user.encode('utf-8'),
            bcrypt.gensalt(12)
        )
        return password_user_hash
    
    @staticmethod
    def check_password(plain_password: str, hashed_password_str: str) -> bool:
        try:
            plain_bytes = plain_password.encode('utf-8')
            
            hashed_bytes = hashed_password_str.encode('utf-8')
            
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception as e:
            logging.warning(f"Erro ao verificar senha (hash inválido?): {e}")
            return False
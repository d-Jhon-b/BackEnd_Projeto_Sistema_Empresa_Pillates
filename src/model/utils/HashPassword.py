import bcrypt # Para hashing de senha
import json # Para tratamento de dados

class HashPassword():
    @staticmethod
    def hash_password(password_user):
        password_user_hash = bcrypt.hashpw(
            password_user.encode('utf-8'),
            bcrypt.gensalt(5)
        )
        return password_user_hash
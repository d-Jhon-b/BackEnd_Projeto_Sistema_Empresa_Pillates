# scripts/hash_password.py

import sys
from passlib.context import CryptContext

# Usa o mesmo contexto de criptografia do nosso serviço de autenticação
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/hash_password.py 'sua_senha_aqui'")
        sys.exit(1)
    
    password_to_hash = sys.argv[1]
    hashed_password = get_password_hash(password_to_hash)
    
    print("Senha original:", password_to_hash)
    print("Senha com Hash:", hashed_password)
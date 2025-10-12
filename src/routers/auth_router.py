# src/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importa as dependências (conexão, schemas, serviços, etc.)
from src.database.connPostGre import get_postgre_session
from src.schemas.user_schemas import UserLoginSchema
from src.repository.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.core.security import create_access_token


# Cria uma instância do APIRouter
router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Funções de Injeção de Dependência ---
# O FastAPI usará essas funções para criar e injetar nossas classes
def get_user_repository(db: AsyncSession = Depends(get_postgre_session)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)

# --- Endpoint de Login ---
@router.post("/login", response_model=dict)
async def login_for_access_token(
    form_data: UserLoginSchema, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Endpoint para autenticar um usuário e retornar um token de acesso.
    """
    # Chama o serviço para autenticar o usuário com o email e senha fornecidos
    user = await auth_service.authenticate_user(email=form_data.email, password=form_data.password)
    
    # Se o serviço retornar None, significa que as credenciais são inválidas
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Lógica para criar o token JWT (simplificada por enquanto)
    # Em um projeto real, a criação do token seria mais complexa,
    # envolvendo uma chave secreta e tempo de expiração.
    access_token = create_access_token(subject=user.endereco_email)
    
    return {"access_token": access_token, "token_type": "bearer"}
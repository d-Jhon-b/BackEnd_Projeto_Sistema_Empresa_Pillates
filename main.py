from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database.connPostGre import POSTGRE_DB_CONNECTOR
from src.routers import auth_router # Importa nosso novo roteador

# Função de lifespan para gerenciar a conexão com o banco de dados
@asynccontextmanager
async def lifespan(app: FastAPI):

    
    # Código a ser executado na inicialização (startup)
    print("Iniciando a aplicação...")
    POSTGRE_DB_CONNECTOR.setup_engine()
    yield
    # Código a ser executado no encerramento (shutdown)
    print("Encerrando a aplicação...")
    await POSTGRE_DB_CONNECTOR.disconnect_db()

# Cria a instância da aplicação FastAPI com o lifespan
app = FastAPI(
    title="API do Sistema de Pilates",
    description="API para gerenciar o estúdio de pilates.",
    version="1.0.0",
    lifespan=lifespan
)

# Inclui o roteador de autenticação na aplicação principal
app.include_router(auth_router.router)

# Endpoint raiz para um teste rápido
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do SIG Pilates!"}
from fastapi import FastAPI
from src.router import user_router # 1. Importa o seu router de usuários

app = FastAPI(
    title="API do Sistema de Pilates",
    description="API para gerenciamento de usuários, aulas e estúdios.",
    version="1.0.0"
)

app.include_router(user_router.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz que retorna uma mensagem de boas-vindas.
    Útil para verificar se a API está funcionando.
    """
    return {"message": "Bem-vindo à API do Sistema de Pilates!"}
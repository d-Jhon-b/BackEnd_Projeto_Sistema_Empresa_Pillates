from fastapi import FastAPI
from src.router import (
    auth_router, 
    aluno_router, 
    instrutor_router, 
    colaborador_router, 
    user_router, 
    agenda_router,
    estudio_router,
    excecao_router,
    aula_router,
    solicitacao_router,
    plano_router,
    adesao_plano_router,
    contrato_router,
    pagamento_router,
    adesao_router,
    agenda_aluno_router
)
from src.database.connMongo import MongoConnectionManager 
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de Contexto para eventos de startup e shutdown.
    """
    print("Iniciando serviços (Lifespan)...")
    try:
        await MongoConnectionManager.connect()
    except Exception as e:
        print(f"ATENÇÃO: Conexão com MongoDB pode ter falhado no Lifespan: {e}")
        
    yield 
    
    print("Fechando serviços (Lifespan)...")
    await MongoConnectionManager.close()
    print("Conexão com MongoDB Atlas fechada.")

app = FastAPI(
    title="API do Sistema de Pilates",
    description="API para gerenciamento de usuários, aulas e estúdios.",
    version="1.0.0",
    lifespan=lifespan
)
origins = [
    "http://localhost:3000",  
    "http://localhost:3001",  
    "http://localhost:5173",  
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],   
    allow_headers=["*"],   
)
app.include_router(auth_router.router)#ok
app.include_router(solicitacao_router.router)
app.include_router(plano_router.router)
app.include_router(aula_router.router)#ok
app.include_router(adesao_router.router)
app.include_router(agenda_router.router)
app.include_router(agenda_aluno_router.router)


app.include_router(aluno_router.router) #ok
app.include_router(instrutor_router.router) #ok
app.include_router(colaborador_router.router) #ok
app.include_router(user_router.router)#ok



app.include_router(estudio_router.router)
app.include_router(excecao_router.router)
app.include_router(adesao_plano_router.router)
app.include_router(contrato_router.router)
app.include_router(pagamento_router.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API do Sistema de Pilates!"}


# src/main.py
from fastapi import FastAPI
from src.router import auth_router, aluno_router, instrutor_router, colaborador_router, user_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="API do Sistema de Pilates",
    description="API para gerenciamento de usuários, aulas e estúdios.",
    version="1.0.0"
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

app.include_router(auth_router.router)
app.include_router(aluno_router.router)
app.include_router(user_router.router)
app.include_router(instrutor_router.router)
app.include_router(colaborador_router.router)
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API do Sistema de Pilates!"}
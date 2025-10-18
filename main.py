import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

# Importa o roteador de usuários que contém a lógica JWT e as rotitas
from src.router.UserRouter import router as user_router

# Configuração de logging #talvez alterar para um arquivo próprio com uma lógica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="API de Gerenciamento de Usuários - Estúdio Pilates",
    description="API robusta para controle de acesso, autenticação JWT e CRUD de usuários.",
    version="1.0.0",
)

original_openapi = app.openapi

JWT_AUTH_NAME = "Bearer (JWT Personalizado)"
OAUTH2_DEFAULT_NAME = "OAuth2PasswordBearer (OAuth2, password)" # Queremos remover/substituir -- titara a desgraça do OAuth2PasswordBearer

def configure_openapi_security() -> Dict[str, Any]:
    # Se o schema já foi gerado (cache), retorna a versão em cache.
    if app.openapi_schema:
        return app.openapi_schema

    # Chama a função original para obter o schema base
    openapi_schema = original_openapi()
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    openapi_schema["components"]["securitySchemes"][JWT_AUTH_NAME] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Insira o token JWT retornado pelo **/v1/users/login** no formato: **Bearer <token>**"
    }


    if OAUTH2_DEFAULT_NAME in openapi_schema["components"]["securitySchemes"]:
        del openapi_schema["components"]["securitySchemes"][OAUTH2_DEFAULT_NAME]       
    if "security" in openapi_schema:
        del openapi_schema["security"]


    for path, methods in openapi_schema["paths"].items():
        for method_name, method_details in methods.items():
            if "security" in method_details:

                # Isso impede que o Swagger insira o OAuth2PasswordBearer novamente.....(não funciona)
                method_details["security"] = [{ JWT_AUTH_NAME: [] }]

    app.openapi_schema = openapi_schema
        
    return openapi_schema

app.openapi = configure_openapi_security
origins = [
    "http://localhost:5000",
    "http://localhost:3000", 
    "http://127.0.0.1:8000",
    "*" # remover dps
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix="/v1")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à APIrest para a SIG_PILLATES.\nAcesse /docs para a documentação."}

if __name__ == "__main__":
    # Comando para rodar: uvicorn main:app --reload
    logging.info("Iniciando o servidor Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

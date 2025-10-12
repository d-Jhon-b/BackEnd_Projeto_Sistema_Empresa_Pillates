import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

# Importa o roteador de usuários que contém a lógica JWT e as rotitas
from src.router.userRouter import router as user_router

# Configuração de logging #talvez alterar para um arquivo próprio com uma lógica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



"""                            """
""" INICIALIZAÇÃO DA APLICAÇÃO """
"""                             """


app = FastAPI(
    title="API de Gerenciamento de Usuários - Estúdio Pilates",
    description="API robusta para controle de acesso, autenticação JWT e CRUD de usuários.",
    version="1.0.0",
)

#Referência para obter o schema base e evitar a recursão.
original_openapi = app.openapi

#ONFIGURAÇÃO OPENAPI PARA SIMPLIFICAR O AUTHORIZE
JWT_AUTH_NAME = "Bearer (JWT Personalizado)"
OAUTH2_DEFAULT_NAME = "OAuth2PasswordBearer (OAuth2, password)" # Queremos remover/substituir -- titara a desgraça do OAuth2PasswordBearer

def configure_openapi_security() -> Dict[str, Any]:
    """
    Configura o schema de segurança JWT para ser exibido no botão 'Authorize'do Swagger UI. 
    A função:
    - Define o esquema HTTP Bearer simples (JWT Personalizado).
     -  Garante que rotas protegidas o utilizem.
    - Impede que rotas públicas (como login) sejam marcadas com cadeado.
    - Remove o esquema OAuth2PasswordBearer de forma agressiva. #não aplicada ainda 14:10-sabádo
    """
    # Se o schema já foi gerado (cache), retorna a versão em cache.
    if app.openapi_schema:
        return app.openapi_schema

    # Chama a função original para obter o schema base
    openapi_schema = original_openapi()
    



    # Define o novo esquema de segurança
    # 1-Garante que o componente 'securitySchemes' exista
    # 2-Adiciona o novo schema de segurança simples (HTTP Bearer)
    
    #-1
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    #2-
    openapi_schema["components"]["securitySchemes"][JWT_AUTH_NAME] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        # Mensagem mais clara para o usuário
        "description": "Insira o token JWT retornado pelo **/v1/users/login** no formato: **Bearer <token>**"
    }


    #Tentativa 1 para retirar a desgraça da validação com user name e 
    if OAUTH2_DEFAULT_NAME in openapi_schema["components"]["securitySchemes"]:
        del openapi_schema["components"]["securitySchemes"][OAUTH2_DEFAULT_NAME]       
    if "security" in openapi_schema:
        del openapi_schema["security"]


    # Esta iteração é CRÍTICA, pois garante que a rota protegida só use o nosso JWT_AUTH_NAME
    for path, methods in openapi_schema["paths"].items():
        for method_name, method_details in methods.items():
            # A chave 'security' indica que a rota está protegida (porque usa Depends(get_current_user))
            if "security" in method_details:

                # Isso impede que o Swagger insira o OAuth2PasswordBearer novamente.....
                method_details["security"] = [{ JWT_AUTH_NAME: [] }]

    #Armazena o schema modificado no cache do app
    app.openapi_schema = openapi_schema
        
    return openapi_schema

app.openapi = configure_openapi_security



"""
Mudar a politica de cors para um arquivo separado e só receber a a validação
"""
origins = [
    "http://localhost:3000",  # Exemplo de um front-end React(espero que seja.... )
    "http://127.0.0.1:8000",
    "*" # Permite todas as origens - retirar quando for aprensetar ou terminar a produção -remover
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
    """Endpoint raiz para testar se a API está online."""
    return {"message": "Bem-vindo à APIrest para a SIG_PILLATES.\nAcesse /docs para a documentação."}

if __name__ == "__main__":
    # Comando para rodar a aplicação: uvicorn main:app --reload
    logging.info("Iniciando o servidor Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Union
from pydantic import EmailStr, Field, BaseModel


from src.model.configModel.all_user_config import UsuarioCompletoConfig 
from src.model.userModel import UserModel
from src.model.configModel.userSettings.valuesUser import NivelAcessoEnum

# Importações de classes de validação específicas do usuário
from src.model.configModel.typeUser.alunos import EstudanteConfig 
from src.model.configModel.typeUser.instrutor import ProfessorConfig 
from src.model.configModel.typeUser.adm import AdministracaoConfig 

# Importa o gerenciador de JWT 
from src.utils.authUtils import auth_manager

#importação para as rotas de login:
from src.router.userRouterConfig.userRouterConfig import LoginRequest,LoginResponse


router = APIRouter(
    prefix="/users",
    tags=["Usuários"],
    responses={404: {"description": "Não encontrado"}},
)

def get_current_user_level(user_payload: Dict[str, Any] = Depends(auth_manager)) -> str:
    """
    Decodifica o token JWT usando auth_manager e extrai o nível de acesso (lv_acesso).
    Se o token for inválido, auth_manager já lança 401.
    """
    level = user_payload.get("lv_acesso")
    if level is None:
        # Se o token estiver válido, mas faltar o nível de acesso (erro na criação do token)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nível de acesso (lv_acesso) não encontrado no token JWT."
        )
    return level


def require_user_creation_permission(user_level: str = Depends(get_current_user_level)):
    """
    Verifica se o nível de acesso do usuário logado é permitido para criar novos usuários.
    Depende de get_current_user_level para obter o nível (via JWT).
    """
    ALLOWED_LEVELS = [
        NivelAcessoEnum.COLABORADOR.value, 
        NivelAcessoEnum.SUPREMO.value 
    ]
    if user_level not in ALLOWED_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissão negada. Apenas {', '.join(ALLOWED_LEVELS)} podem criar novos usuários."
        )
    # Retorna o nível de acesso
    return user_level
    


def get_user_model(executor_level: str = Depends(get_current_user_level)) -> UserModel:
    """
    Instancia o UserModel, injetando o nível de acesso do executor (via JWT) no construtor.
    """
    return UserModel(executor_level)

@router.post(
    "/aluno", 
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any], 
    # require_user_creation_permission garante que o token é válido e que o nível de acesso é suficiente
    dependencies=[Depends(require_user_creation_permission)], 
    summary="Cria um novo usuário do tipo Aluno."
)
async def criar_novo_aluno(
    user_data: EstudanteConfig, 
    user_model: UserModel = Depends(get_user_model) 
):
    dados_para_inserir = user_data.model_dump()
    resultado = user_model.inserir_novo_usuario(dados_para_inserir)
    if resultado['status'] == 'error':
        if "Permissão negada" in resultado['message']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=resultado['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=resultado['message']
            )
    return resultado


@router.post(
    "/instrutor", 
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any], 
    dependencies=[Depends(require_user_creation_permission)], 
    summary="Cria um novo usuário do tipo Instrutor/Professor."
)
async def criar_novo_instrutor(
    user_data: ProfessorConfig, 
    user_model: UserModel = Depends(get_user_model) 
):
    dados_para_inserir = user_data.model_dump()
    resultado = user_model.inserir_novo_usuario(dados_para_inserir)
    if resultado['status'] == 'error':
        if "Permissão negada" in resultado['message']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=resultado['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=resultado['message']
            )
    return resultado


@router.post(
    "/administracao", 
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any], 
    # dependencies=[Depends(require_user_creation_permission)], 
    summary="Cria um novo usuário de Administração (Colaborador/Supremo)."
)
async def criar_novo_administrador(
    user_data: AdministracaoConfig, 
    user_model: UserModel = Depends(get_user_model) 
    # user_model: UserModel = Depends(lambda: UserModel(NivelAcessoEnum.SUPREMO.value))

):
    dados_para_inserir = user_data.model_dump()
    resultado = user_model.inserir_novo_usuario(dados_para_inserir)
    if resultado['status'] == 'error':
        if "Permissão negada" in resultado['message']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=resultado['message']
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=resultado['message']
            )
    return resultado


@router.post(
    "/login", 
    response_model=LoginResponse, 
    summary="Realiza o login do usuário e retorna dados de autenticação (JWT)."
)
async def fazer_login_endpoint(
    request: LoginRequest,
    # user_model: UserModel = Depends(lambda: UserModel(executor_level=NivelAcessoEnum.COLABORADOR.value))
    user_model: UserModel = Depends(lambda: UserModel(NivelAcessoEnum.ANONIMO.value))
    # user_model: UserModel = Depends(lambda: UserModel(executor_level=None))
):
    
    usuario_logado = user_model.fazer_login(request.email, request.senha)
    if usuario_logado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas (Email ou Senha incorretos)."
        )

    jwt_payload = {
        "id_user": usuario_logado["id_user"],
        "lv_acesso": usuario_logado["lv_acesso"]
    }

    access_token = auth_manager.create_access_token(data=jwt_payload)
    
    return LoginResponse(
        message="Login realizado com sucesso.",
        access_token=access_token,
        token_type="bearer",
        user_data=usuario_logado
    )





#Rota de Teste de Autorização - REMOVIDO
# @router.get("/me", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
# def read_users_me(
#     # A dependência auth_manager faz a validação do token e retorna o payload
#     current_user_level: str = Depends(get_current_user_level)
# ):
#     """
#     Rota protegida. Retorna o nível de acesso do usuário autenticado.
#     Se o token for inválido, o auth_manager irá lançar HTTPException 401.
#     """
#     return {"message": "Token Válido", "current_user_level": current_user_level}

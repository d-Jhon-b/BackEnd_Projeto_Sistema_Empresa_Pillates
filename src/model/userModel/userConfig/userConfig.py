from pydantic import BaseModel, Field, BeforeValidator, ConfigDict, ValidationError, model_validator
from typing import Union, Optional, Any, Annotated
from enum import Enum
from bson import ObjectId
from datetime import date

from src.model.userModel.detailsConfig.validation import UserProfilePayload



class TipoDocumento(str, Enum):
    CPF = 'cpf'
    CNPJ = 'cnpj'

class LevelAccess(str,Enum):
    SUPREMO = 'supremo'
    COLABORADOR = 'colaborador'
    INSTRUTOR = 'instrutor'
    ALUNO = 'aluno'
    #        sa.Column('lv_acesso', sa.Enum('supremo', 'colaborador', 'instrutor','aluno',  name='lv_acesso_enum')),


class CustomTypes:
    
    @staticmethod
    def _validate_objectid(v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError(f"Não é um ID de objeto válido: {v}")

    # Definido como um atributo de classe
    PydanticObjectId = Annotated[
        ObjectId,
        BeforeValidator(_validate_objectid)
    ]
    


class UserConfig(BaseModel):

    """CARACTERISTICAS DOS BANCOS"""
    id_user_post_gre: Optional[int]=Field(None, title='ID para banco de dados Relacional')
    id_user_mongo: Optional[CustomTypes.PydanticObjectId]=Field(None, alias="_id", title="ID para MongoDB")
    
    """DADOS DO USUARIO"""
    name_user: str = Field(..., max_length=255, title='Nome Completo' )
    foto_user: str= Field(None,max_length=255,title='hash da foto/imagem')
    nasc_user: date = Field(...,title='Data de Nascimento.\nEXEMPLO: (YYYY-MM-DD)')
    tipo_doc_user: TipoDocumento = Field(..., title='Tipo de documento')
    num_doc_user:  str=Field(..., max_length=14, title=f'Número do Documento') 
    
    """NIVEL DE ACESSO"""
    lv_acesso: LevelAccess = Field(...,title='Nível de acesso')
    tipo_logica:Optional[str] = Field(None)
    
    """Tipo de acesso """
    tipo_email_user : str=Field(..., title='tipo do email do user')
    email_user:str=Field(..., title='Email para login do user')
    senha_user:str=Field(..., title="senha do user")


    profissao_user: Optional[str] = Field(None)
    historico_medico: Optional[str] = Field(None)


    details:UserProfilePayload = Field(default_factory=UserProfilePayload)
    
    model_config = ConfigDict(
        # 1. ESSENCIAL PARA MONGODB: Como serializar ObjectId para JSON
        # 2. ESSENCIAL PARA MONGODB/ENTRADA: Permite usar o alias "_id"
        # 3. ESSENCIAL PARA POSTGRESQL/SQLAlchemy: Permite instanciar o modelo 
        # diretamente de um objeto ORM (Substitui 'orm_mode=True')


        json_encoders={ObjectId: str},
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        extra='allow', 

    )


    @model_validator(mode='before')
    @classmethod
    def group_and_validate_details(cls, data: Any) -> Any:
        """
        Este validador executa ANTES da validação principal.
        Ele agrupa os dados de detalhes (contatos, emails, endereços)
        e os valida usando o modelo UserProfileDetails.
        """
        if not isinstance(data, dict):
            return data # Não faz nada se não for um dicionário
        
        # Pega as listas de detalhes do payload de entrada
        details_data = {
            "contatos": data.get("contatos", []),
            # "emails": data.get("emails", []),
            "enderecos": data.get("enderecos", []),
        }
        
        try:
            # Chama a classe de validação dos detalhes
            validated_details = UserProfilePayload(**details_data)
            
            # Adiciona os detalhes validados de volta aos dados principais
            # sob a chave 'details' para o modelo UserConfig processar.
            data['details'] = validated_details
            
            return data
            
        except ValidationError as e:
            # Se a validação dos detalhes falhar, levanta um erro para
            # interromper o processo.
            # (Poderia ser um raise e mais específico, mas ValueError é simples)
            raise ValueError(f"Erro na validação dos detalhes do perfil: {e}")
        
    @model_validator(mode='after') # Usar 'after' é mais seguro aqui
    def check_required_role_fields(self) -> 'UserConfig':
        """Valida se os campos obrigatórios para um papel específico foram fornecidos."""
        if self.lv_acesso == LevelAccess.ALUNO:
            if self.historico_medico is None:
                raise ValueError("O campo 'historico_medico' é obrigatório para alunos.")
        # Adicione outras validações de papel aqui, se necessário
        return self







# dados_validos = {
#     "name_user": "Ana Carolina",
#     "nasc_user": "1988-03-20",
#     "tipo_doc_user": "cpf",
#     "num_doc_user": "111.444.777-05", # A validação de formato não está ativa, então qualquer string serve
#     "lv_acesso": "colaborador",
    
#     # --- CAMPOS OBRIGATÓRIOS ADICIONADOS ---
#     "email_user": "ana.carolina@email.com",
#     "senha_user": "umaSenhaForteEComplexa123!",
#     # --- FIM DA ADIÇÃO ---

#     "contatos": [
#         {"tipo_contato": "RESIDENCIAL", "numero_contato": "+55 11 98765-4321"}
#     ],
    
#     "enderecos": [] # Lista vazia também é válida
# }

# # --- EXECUÇÃO DO TESTE ---
# try:
#     user_validado = UserConfig(**dados_validos)
#     print(" Usuário e seus detalhes foram validados com sucesso!")
#     print("Tipo de contato validado:", user_validado.details.contatos[0].tipo_contato)
#     print("Email principal do usuário:", user_validado.email_user)

# except (ValidationError, ValueError) as e:
#     print(f"Falha inesperada: {e}")
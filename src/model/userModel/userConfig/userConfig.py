from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing import Union, Optional, Any, Annotated
from enum import Enum
from bson import ObjectId
from datetime import date



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








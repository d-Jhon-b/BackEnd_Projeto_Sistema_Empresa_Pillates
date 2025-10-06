from pydantic import BaseModel, Field
from typing import Union, Optional, Any
from enum import Enum
from bson import ObjectId
from datetime import date


class TipoDocumento(str.lower(), Enum):
    CPF = 'cpf'
    CNPJ = 'cnpj'

class LevelAccess(str.lower(),Enum):
    SUPREMO = 'supremo'
    COLABORADOR = 'colaborador'
    INSTRUTOR = 'instrutor'
    ALUNO = 'aluno'
    #        sa.Column('lv_acesso', sa.Enum('supremo', 'colaborador', 'instrutor','aluno',  name='lv_acesso_enum')),


class PydanticObjectId(str):
    @classmethod
    def __get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v:Any):
        if not isinstance(v, ObjectId):
            raise TypeError('É necessário um objectID')
        return (str)
    


class UserConfig(BaseModel):
    idUserPostGre:Optional[int]=Field(None, title='ID para banco de dados Relacional')
    idUserMongo: Optional[PydanticObjectId]=Field(None, alias="_id", title="ID para MongoDB")
    nomeUser: Optional[str] = Field(..., max_length=255, title='Nome Completo' )
    fotoUser: Optional[str]= Field(None,max_digits=26,title='has da foto/imagem')
    nascUser: date = Field(...,title='Data de Nascimento.\nEXEMPLO: (YYYY-MM-DD)')
    tipoDocUser: TipoDocumento = Field(..., title='Tipo de documento')
    numDocUser:  str=Field(..., max_length=14, title=f'Número do Documento') 
    lvAccess: LevelAccess = Field(...,title='Nível de acesso')
    


    class Config:
        """Configurações Pydantic."""
        
        # Permite que o Pydantic reconheça tanto o campo 'mongo_id' quanto o alias '_id'
        populate_by_name = True 
        
        # Converte o ObjectId do Mongo para string quando o modelo é exportado para JSON
        json_encoders = {
            ObjectId: str
        }
        
        # Garante que os valores das Enums ('cpf', 'SUPREMO') sejam usados em vez do objeto Enum
        use_enum_values = True 
        
        # Exemplo para a documentação (swagger/openapi)
        schema_extra = {
            "example": {
                "nameUser": "Alice da Silva",
                "nascUser": "1990-05-15",
                "tipoDocUser": "cpf",
                "numDocUser": "12345678901",
                "lvAccess": "COLABORADOR",
            }
        }





from pydantic import BaseModel, Field
from typing import Optional, Any
from src.schemas.agenda_schemas import PyObjectId # Se precisar do PyObjectId


class EstudioBaseSchema(BaseModel):
    endereco_estudio: str = Field(..., alias="endereco", max_length=255)
    cep_estudio: str = Field(..., alias="cep", min_length=8, max_length=8)
    # Este campo no PostgreSQL não parece ter utilidade direta na API de criação, mas vamos mantê-lo se for um requisito de validação
    mongo_registros_estudio: str = Field(..., alias="mongoRegistro") 
    
    model_config = { 
        'populate_by_name': True, 
        'json_schema_extra': {
            "example": {
                "endereco": "Rua das Flores, 123",
                "cep": "01000000",
                "mongoRegistro": "studiomongo_101" 
            }
        }
    }

class EstudioCreateSchema(EstudioBaseSchema):
    """ Usado para o POST (Criação) """
    pass
    
class EstudioUpdateSchema(BaseModel):
    """ Usado para o PATCH (Atualização parcial) """
    endereco_estudio: Optional[str] = Field(None, alias="endereco", max_length=255)
    cep_estudio: Optional[str] = Field(None, alias="cep", min_length=8, max_length=8)
    mongo_registros_estudio: Optional[str] = Field(None, alias="mongoRegistro") 

    model_config = { 'populate_by_name': True }


class EstudioResponseSchema(EstudioBaseSchema):
    """ Retorna o documento completo com o ID do PostgreSQL. """
    id_estudio: int = Field(..., alias="EstudioID") # Chave primária do PostgreSQL
    
    model_config = {
        'from_attributes': True,
        'populate_by_name': True
    }
from pydantic import BaseModel, Field
from typing import Optional, Any, Callable
from datetime import date, datetime
from bson import ObjectId
from src.schemas.agenda_schemas import PyObjectId 

class ExcecaoBaseSchema(BaseModel):
    """
    Schema base para criar ou atualizar uma Exceção de Cronograma.
    Representa um dia que o estúdio está INDISPONÍVEL.
    """
    
    data_excecao: date = Field(..., alias="dataExcecao") 
    # ID do estúdio afetado (PostgreSQL ID)
    fk_id_estudio: int = Field(..., alias="EstudioID")
    
    # Motivo da exceção (Ex: Aniversário, Feriado, Manutenção)
    descricao: str = Field(..., alias="motivoExcecao", max_length=200)
    
    # Status: 1 = Indisponível (Fechado), 0 = Disponível (Revertido/Reaberto)
    status_indisponibilidade: int = Field(
        1, 
        alias="statusIndisponibilidade", 
        ge=0, 
        le=1
    ) 
    
    model_config = { 
        'populate_by_name': True, 
        'json_schema_extra': {
            "example": {
                "dataExcecao": "2026-03-25",
                "EstudioID": 101,
                "motivoExcecao": "Aniversário do Proprietário",
                "statusIndisponibilidade": 1 
            }
        }
    }

class ExcecaoCreateSchema(ExcecaoBaseSchema):
    """ Usado para o POST (Criação) """
    pass
    
class ExcecaoUpdateSchema(BaseModel):
    descricao: Optional[str] = Field(None, alias="motivoExcecao", max_length=200)
    status_indisponibilidade: Optional[int] = Field(None, alias="statusIndisponibilidade", ge=0, le=1)

    model_config = { 'populate_by_name': True }


class ExcecaoResponseSchema(ExcecaoBaseSchema):
    """ Retorna o documento completo com o ID do MongoDB. """
    id: PyObjectId = Field(alias="_id", default=None)
    
    model_config = {
        'from_attributes': True,
        'json_encoders': {
            ObjectId: str,
            # Converte a data para o formato ISO (YYYY-MM-DD)
            date: lambda v: v.isoformat() 
        },
        'populate_by_name': True,
        'arbitrary_types_allowed': True
    }
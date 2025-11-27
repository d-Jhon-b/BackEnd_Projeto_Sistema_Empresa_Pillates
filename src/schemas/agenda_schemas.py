from pydantic import BaseModel, Field
from typing import Optional, List, Any, Callable
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema as cs 

class PyObjectId(ObjectId):
    """ Customiza a manipulação do ObjectId para Pydantic v2. """
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Callable[..., cs.CoreSchema]) -> cs.CoreSchema:
        
        validation_schema = cs.chain_schema(
            [
                # Tenta converter str/bytes/ObjectId -> ObjectId
                cs.no_info_plain_validator_function(cls.validate), 
                # Garante que o resultado final é um ObjectId
                cs.is_instance_schema(ObjectId) 
            ]
        )
        
        # Removemos o argumento 'serialization' daqui. A serialização será feita no model_config.
        return cs.json_or_python_schema(
            python_schema=validation_schema,
            json_schema=cs.str_schema(),
        )
        
    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, (str, bytes)):
            try:
                if isinstance(v, str) and not ObjectId.is_valid(v):
                    raise ValueError("ID inválido do MongoDB (ObjectId)")
                return ObjectId(v)
            except Exception as e:
                raise ValueError(f"Não foi possível converter para ObjectId: {v}") from e
        
        raise TypeError(f"ObjectId deve ser string, bytes ou ObjectId, não {type(v)}")


class AgendaAulaCreateSchema(BaseModel):
    fk_id_aula: int = Field(..., alias="AulaID") 
    fk_id_professor: int = Field(..., alias="professorResponsavel")
    fk_id_estudio: int = Field(..., alias="EstudioID")
    
    titulo_aula: str = Field(..., max_length=150, alias="tituloAulaCompleto")

    disciplina: str = Field(..., max_length=100)
    data_aula: datetime = Field(..., alias="dataAgendaAula")
    desc_aula: Optional[str] = Field(None, alias="descAgendaAula")
    duracao_minutos: int = Field(..., ge=5, alias="duracaoAula") 
    participantes_ids: List[int] = Field(default_factory=list, alias="participantes")

    model_config = { 'populate_by_name': True }


# Schema de Resposta (Ajustado para serialização explícita)
class AgendaAulaResponseSchema(AgendaAulaCreateSchema):
    id: PyObjectId = Field(alias="_id", default=None)
    model_config = {
        'from_attributes': True, 
        # Serializador explícito: Converte qualquer ObjectId encontrado para str no JSON.
        'json_encoders': {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        },
        'populate_by_name': True,
        'arbitrary_types_allowed': True
    }




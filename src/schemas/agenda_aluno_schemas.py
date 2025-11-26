from pydantic import BaseModel, Field,ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum
# from bson import ObjectId
from bson import ObjectId # 🎯 IMPORTAÇÃO CORRETA E PADRÃO PARA O OBJETO REAL
from src.schemas.agenda_schemas import PyObjectId

class StatusPresencaEnum(str, Enum):
    AGENDADA = "Agendada" 
    PRESENTE = "Presente"
    FALTA = "Falta"
    REAGENDADA = "Reagendada"
    AUSENCIA_JUSTIFICADA = "Ausência Justificada"

class AgendaAlunoCreate(BaseModel):
    """Schema para a criação do registro da aula na agenda do aluno."""
    fk_id_estudante: int = Field(..., alias="EstudanteID")
    fk_id_aula_sql: int = Field(..., alias="AulaID")
    fk_id_professor_sql: int = Field(..., alias="ProfessorID")
    
    data_hora_aula: datetime = Field(..., alias="DataHoraAula")
    disciplina: str
    
    status_presenca: StatusPresencaEnum = Field(StatusPresencaEnum.AGENDADA, alias="StatusPresenca")
    
    fk_id_estudio: int = Field(..., alias="EstudioID")


class AgendaAlunoUpdate(BaseModel):
    """Schema para atualização (principalmente Presença e Evolução)."""
    
    status_presenca: Optional[StatusPresencaEnum] = Field(None, alias="StatusPresenca")
    
    nota_evolucao: Optional[str] = Field(None, alias="NotaEvolucao")
    
    # Anexos (links para S3/Cloud Storage, se for o caso)
    anexos_links: Optional[List[str]] = Field(None, alias="AnexosLinks")

    

class AgendaAlunoResponse(BaseModel):
    """Schema de resposta, incluindo o ID do MongoDB."""
    # id: Optional[ObjectId] = Field(None, alias="_id", default_factory=None) 
    id: Optional[PyObjectId] = Field(None, alias="_id", default_factory=None) 
    # id: Optional[str] = Field(None, alias="_id",default=None) 
    AulaID: int
    ProfessorID: int
    EstudioID: int
    DataHoraAula: datetime
    disciplina: str
    StatusPresenca: StatusPresencaEnum
    NotaEvolucao: Optional[str] = None
    AnexosLinks: Optional[List[str]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True, 
        json_encoders={
            ObjectId: str 
        }
    )
    # class Config:
    #     populate_by_name = True



    
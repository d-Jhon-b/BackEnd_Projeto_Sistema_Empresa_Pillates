from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class StatusPresencaEnum(str, Enum):
    PRESENTE = "Presente"
    FALTA = "Falta"
    REAGENDADA = "Reagendada"
    AUSENCIA_JUSTIFICADA = "Ausência Justificada"

class AgendaAlunoCreate(BaseModel):
    """Schema para a criação do registro da aula na agenda do aluno."""
    # Chaves Estrangeiras (SQL IDs)
    fk_id_estudante: int = Field(..., alias="EstudanteID")
    fk_id_aula_sql: int = Field(..., alias="AulaID")
    fk_id_professor_sql: int = Field(..., alias="ProfessorID")
    
    # Dados da Aula (para consulta rápida)
    data_hora_aula: datetime = Field(..., alias="DataHoraAula")
    disciplina: str
    
    # Campos dinâmicos (iniciais)
    status_presenca: StatusPresencaEnum = Field(StatusPresencaEnum.FALTA, alias="StatusPresenca")
    # 'FALTA' é o padrão, pois a presença só é marcada após a aula.
    
    # Opcional: Referência ao Estúdio/Unidade (Para multisite)
    fk_id_estudio: int = Field(..., alias="EstudioID")


class AgendaAlunoUpdate(BaseModel):
    """Schema para atualização (principalmente Presença e Evolução)."""
    
    # Atualizado pelo Instrutor/Admin
    status_presenca: Optional[StatusPresencaEnum] = Field(None, alias="StatusPresenca")
    
    # Atualizado pelo Instrutor/Admin após a aula
    nota_evolucao: Optional[str] = Field(None, alias="NotaEvolucao")
    
    # Anexos (links para S3/Cloud Storage, se for o caso)
    anexos_links: Optional[List[str]] = Field(None, alias="AnexosLinks")

class AgendaAlunoResponse(BaseModel):
    """Schema de resposta, incluindo o ID do MongoDB."""
    id_registro: str = Field(..., alias="_id")
    EstudanteID: int
    AulaID: int
    ProfessorID: int
    EstudioID: int
    DataHoraAula: datetime
    disciplina: str
    StatusPresenca: StatusPresencaEnum
    NotaEvolucao: Optional[str] = None
    AnexosLinks: Optional[List[str]] = None

    class Config:
        populate_by_name = True
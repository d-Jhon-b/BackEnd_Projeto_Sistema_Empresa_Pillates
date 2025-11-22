from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
# Importando o Enum necessário do seu arquivo de schemas de usuário
from src.schemas.user_schemas import ProfessorResponse, EstudanteResponse # Supondo que você terá um EstudanteResponse




# --- Emuns para tipo de aula que é aplicada:

class TipoAulaEnum(str, Enum):
    NORMAL = 'normal'
    EXPERIMENTAL = 'experimental'
    REPOSICAO='reposicao'
    
# ---Schemas de resposta  ---

class EstudanteAulaResponse(BaseModel):
    """Representa o dado da tabela de associação (matrícula)."""
    fk_id_estudante: int
    fk_id_aula: int
    tipo_de_aula: TipoAulaEnum
    # estudante: EstudanteResponse # Requer um Schema de Estudante
    
    class Config:
        from_attributes = True


# --- SCHEMAS DE ENTRADA (PAYLOADS) ---

class AulaCreate(BaseModel):
    """Payload para criação de uma nova aula."""
    data_aula: datetime
    titulo_aula: str = Field(..., max_length=255)
    desc_aula: Optional[str] = Field(None, max_length=255)
    fk_id_estudio: int 
    fk_id_professor: int
    fk_id_professor_substituto: Optional[int] = None
    disciplina: Optional[str] = None # Adicione este campo! 
    duracao_minutos: Optional[int] = Field(..., ge=5) 
    estudantes_a_matricular: Optional[List[int]] = None 

class AulaUpdate(BaseModel):
    """Payload para atualização dos dados de uma aula."""
    # Todos os campos são opcionais para o update
    data_aula: Optional[datetime] = None
    titulo_aula: Optional[str] = Field(None, max_length=255)
    desc_aula: Optional[str] = Field(None, max_length=255)
    fk_id_estudio: Optional[int] = None
    fk_id_professor: Optional[int] = None
    fk_id_professor_substituto: Optional[int] = None
    
# --- Schema para matricula em uma aula

class MatriculaCreate(BaseModel):
    """Payload para matricular um único estudante em uma aula existente."""
    fk_id_estudante: int
    tipo_de_aula: TipoAulaEnum = TipoAulaEnum.NORMAL

#---Chemas para reagendamento de aula
class ReagendarCreate(BaseModel):
    fk_id_estudante: int


#-------------Schemas para respotas de aula
class AulaResponse(BaseModel):
    """Schema de resposta para uma aula (Inclui relacionamentos ORM)."""
    id_aula: int
    data_aula: datetime
    titulo_aula: str
    desc_aula: Optional[str]
    fk_id_estudio: int
    fk_id_professor: int
    fk_id_professor_substituto: Optional[int]
    
    estudantes_associacao: List[EstudanteAulaResponse] = []     
    # professor: Optional[ProfessorResponse] = None 
    class Config:
        from_attributes = True




#--------------Para aulas Recorrentes:
class DiaSemanaEnum(str, Enum):
    SEGUNDA = "Segunda-feira"
    TERCA = "Terça-feira"
    QUARTA = "Quarta-feira"
    QUINTA = "Quinta-feira"
    SEXTA = "Sexta-feira"
    SABADO = "Sábado"
    DOMINGO = "Domingo"

class AulaRecorrenteCreate(BaseModel):
    """Schema para criação de aulas com recorrência semanal."""
    
    # Campos da Aula (Base)
    fk_id_professor: int
    fk_id_estudio: int
    titulo_aula: str
    desc_aula: Optional[str] = None
    # capacidade_max: int
    duracao_minutos: int
    disciplina: str
    
    # NOVOS CAMPOS PARA RECORRÊNCIA
    dia_da_semana: DiaSemanaEnum = Field(..., description="Dia da semana para agendamento.")
    horario_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Horário de início no formato 'HH:MM'.")
    data_inicio_periodo: date = Field(..., description="Data de início do período de recorrência.")
    data_fim_periodo: date = Field(..., description="Data de fim do período de recorrência (inclusive).")
    
    # Opcional: Estudantes iniciais
    estudantes_a_matricular: Optional[List[int]] = []
    
    @field_validator('data_fim_periodo')
    def validate_dates(cls, v, info):
        if 'data_inicio_periodo' in info.data and v <= info.data['data_inicio_periodo']:
            raise ValueError("A data final do período deve ser posterior à data inicial.")
        return v
    

class MatriculaSeriesCreate(BaseModel):
    """Payload para matricular um estudante em todas as aulas futuras de uma série (por título)."""
    fk_id_estudante: int = Field(..., alias="EstudanteID")
    titulo_aula: str = Field(..., alias="TituloAula")
    tipo_de_aula: TipoAulaEnum = Field(TipoAulaEnum.NORMAL, alias="TipoAula")
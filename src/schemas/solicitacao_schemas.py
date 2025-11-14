from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from src.schemas.user_schemas import UserBaseSchema
from enum import Enum
from datetime import datetime

# class DeterminarHoraCriacao():
#     def deter

class TipoDeSolicitacaoEnum(str, Enum):
    AULA = "aula"
    PLANO  = 'plano'
    PAGAMENTO = 'pagamento'
    OUTROS = 'outros'

class StatusSolcitacaoEnum(str, Enum):
    EM_ESPERA='em espera'
    ATENDIDA='atendida'
    RECUSADA='recusada'


class SolicitacoesBase(BaseModel):
    fk_id_user: int #Optional[int]
    fk_id_estudio: int #Optional[int]
    menssagem: Optional[str] = None
    class Config:
        from_attributes=True

class SolicitacaoCreate(SolicitacoesBase):
    tipo_de_solicitacao: TipoDeSolicitacaoEnum = Field(...)
    data_criacao: datetime = Field(default_factory=datetime.now)

    # status_solicitacao #Não precisa usar, dado que o DB por padrão define como: "em espera"

    
class SolicitacaoUpdate(BaseModel):
    status_solicitacao: StatusSolcitacaoEnum =Field(...)
    data_resposta: datetime=Field(default_factory=datetime.now)

class Solicitacao(SolicitacoesBase):
    # Schema completo para retorno (inclui status e data)
    id_solicitacao: int # Chave primária
    tipo_de_solicitacao: TipoDeSolicitacaoEnum
    status_solicitacao: StatusSolcitacaoEnum
    data_criacao: datetime

    
# soli_update = SolicitacaoUpdate(status_solicitacao=StatusSolcitacaoEnum.RECUSADA)
# print(f"\nTeste SolicitacaoUpdate:")
# print(soli_update.model_dump())

# soli_create = SolicitacaoCreate(
#     fk_id_user=1, 
#     fk_id_estudio=101, 
#     tipo_de_solicitacao=TipoDeSolicitacaoEnum.AULA,
#     menssagem="Gostaria de agendar uma aula experimental."
# )
# print(f"\nTeste SolicitacaoCreate:")
# print(soli_create.model_dump())
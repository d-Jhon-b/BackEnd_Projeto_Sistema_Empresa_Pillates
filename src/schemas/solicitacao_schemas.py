from pydantic import BaseModel, Field,model_validator
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

class AcaoSolicitacaoPlanoEnum(str, Enum):
    MUDANCA_PLANO = 'MUDANCA_PLANO'
    CANCELAMENTO_PLANO = 'CANCELAMENTO_PLANO'
    RENOVACAO_PLANO = 'RENOVACAO_PLANO'

class AcaoSolicitacaoAulaEnum(str, Enum):
    AGENDAMENTO = 'AGENDAMENTO'
    REAGENDAMENTO = 'REAGENDAMENTO'
    CANCELAMENTO ='CANCELAMENTO'
# class SolicitacaoCreatePayload(BaseModel):
#     menssagem: Optional[str] = None
#     tipo_de_solicitacao: TipoDeSolicitacaoEnum

class SolicitacaoCreatePayload(BaseModel):
    menssagem: Optional[str] = None
    tipo_de_solicitacao: TipoDeSolicitacaoEnum = Field(..., description="Tipo da solicitação (aula, plano, pagamento, outros).")    
    acao_solicitacao_plano: Optional[AcaoSolicitacaoPlanoEnum] = Field(None, description="Ação específica se tipo_de_solicitacao for 'plano'.")
    acao_solicitacao_aula:Optional[AcaoSolicitacaoAulaEnum] = Field(None, description="Ação específica se tipo_de_solicitacao for 'aula'.")
    
    fk_id_aula_referencia: Optional[int] = Field(None, description="ID da aula sugerida")

    data_sugerida: Optional[datetime] = None
    fk_id_novo_plano: Optional[int] = Field(None, description="ID do novo plano padrão, se aplicável.")
    fk_id_novo_plano_personalizado: Optional[int] = Field(None, description="ID do novo plano personalizado, se aplicável.")

    @model_validator(mode='after')
    # def check_plano_fields(self) -> 'SolicitacaoCreatePayload':
    def check_solicitacao_values_fields(self) -> 'SolicitacaoCreatePayload':
        if self.tipo_de_solicitacao == TipoDeSolicitacaoEnum.PLANO:
            if not self.acao_solicitacao_plano:
                raise ValueError("Ação do plano é obrigatória para solicitações de plano.")
            
            if self.fk_id_novo_plano and self.fk_id_novo_plano_personalizado:
                raise ValueError("Apenas um ID de novo plano (Padrão ou Personalizado) pode ser fornecido.")
            
            if self.acao_solicitacao_plano in [AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO, AcaoSolicitacaoPlanoEnum.RENOVACAO_PLANO] and not (self.fk_id_novo_plano or self.fk_id_novo_plano_personalizado):
                raise ValueError("Novo plano é obrigatório para Mudança ou Renovação.")
            
        elif self.tipo_de_solicitacao == TipoDeSolicitacaoEnum.AULA:
            if not self.acao_solicitacao_aula:
                raise ValueError("Ação da aula é obrigatória para solicitações de aula.")

            # if self.acao_solicitacao_aula in [AcaoSolicitacaoAulaEnum.AGENDAMENTO, AcaoSolicitacaoAulaEnum.REAGENDAMENTO] and not self.data_sugerida:
            #      raise ValueError("Data sugerida é obrigatória para AGENDAMENTO ou REAGENDAMENTO de aulas.")
            if self.acao_solicitacao_aula in [AcaoSolicitacaoAulaEnum.REAGENDAMENTO, AcaoSolicitacaoAulaEnum.CANCELAMENTO] and not self.fk_id_aula_referencia:
                raise ValueError(f"ID da aula de referência é obrigatório para {self.acao_solicitacao_aula.value}.")
            
            if self.acao_solicitacao_aula == AcaoSolicitacaoAulaEnum.AGENDAMENTO and self.fk_id_aula_referencia:
                raise ValueError("ID da aula de referência deve ser nulo para AGENDAMENTO de nova aula.")
                
            if self.fk_id_novo_plano or self.fk_id_novo_plano_personalizado:
                raise ValueError("Campos de plano não devem ser preenchidos em solicitações de aula.")
            
            # if self.fk_id_aula_referencia not in [AcaoSolicitacaoAulaEnum.AGENDAMENTO, AcaoSolicitacaoAulaEnum.CANCELAMENTO, AcaoSolicitacaoAulaEnum.REAGENDAMENTO]:
            #     raise ValueError("Valor invalido para uma solicitação relacionada com aula")
            

        return self

class SolicitacoesBase(BaseModel):
    # fk_id_user: int #Optional[int]
    fk_id_estudante: int
    fk_id_estudio: int #Optional[int]
    menssagem: Optional[str] = None
    class Config:
        from_attributes=True

# class SolicitacaoCreate(SolicitacoesBase):
#     tipo_de_solicitacao: TipoDeSolicitacaoEnum = Field(...)
#     data_criacao: datetime = Field(default_factory=datetime.now)

    # status_solicitacao #Não precisa usar, dado que o DB por padrão define como: "em espera"
class SolicitacaoCreate(SolicitacaoCreatePayload, SolicitacoesBase):
    # fk_id_estudante (herdado de SolicitacoesBase)
    # fk_id_estudio (herdado de SolicitacoesBase)
    data_criacao: datetime = Field(default_factory=datetime.now)
    
class SolicitacaoUpdate(BaseModel):
    status_solicitacao: StatusSolcitacaoEnum =Field(...)
    # data_resposta: datetime=Field(default_factory=datetime.now)
# class SolicitacaoUpdatePayload(SolicitacaoUpdate):

class SolicitacaoResponseSchema(SolicitacoesBase):
    # id_solicitacao: int
    # tipo_de_solicitacao: TipoDeSolicitacaoEnum
    # status_solicitacao: StatusSolcitacaoEnum
    # data_criacao: datetime
    # data_resposta: Optional[datetime]
    id_solicitacao: int
    tipo_de_solicitacao: TipoDeSolicitacaoEnum
    status_solicitacao: StatusSolcitacaoEnum
    data_criacao: datetime
    data_resposta: Optional[datetime]
    
    # NOVOS CAMPOS DO BANCO
    acao_solicitacao_plano: Optional[AcaoSolicitacaoPlanoEnum] = None
    fk_id_novo_plano: Optional[int] = None
    fk_id_novo_plano_personalizado: Optional[int] = None





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
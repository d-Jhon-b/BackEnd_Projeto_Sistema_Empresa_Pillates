from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.schemas.contrato_schemas import StatusContratoEnum
from src.schemas.plano_schemas import PlanoResponse

class PlanoDetalhe(BaseModel):
    """Informações essenciais do Plano para exibição no frontend."""
    nome_plano: str = Field(..., description="Nome do plano.")
    
    modalidade: str = Field(..., description="Modalidade de aulas (Ex: 3x_semana ou descrição livre).")
    
    tipo_plano: str = Field(..., description="Tipo/Vigência do Plano (Ex: mensal, livre).")
    descricao_plano:Optional[str]
    valor_final_contrato: float = Field(..., description="Valor final (Numeric 10,2) negociado no Contrato.")
    qtde_aulas_totais_plano: int = Field(..., description="Total de aulas do plano contratado.")
    
    class Config:
        from_attributes = True

class PlanoAtivoDetalhadoResponse(BaseModel):
    """Retorno otimizado para a tela 'Meu Plano', combinando Contrato e Plano."""
    id_contrato: int
    data_vencimento: datetime = Field(..., alias='data_termino', description="Data de término do contrato (Vencimento).")
    aulas_restantes: int
    status_contrato: StatusContratoEnum
    
    detalhes_plano: PlanoDetalhe = Field(..., description="Informações específicas do plano (nome, valor, modalidade).")
    
    class Config:
        from_attributes = True
        populate_by_name = True
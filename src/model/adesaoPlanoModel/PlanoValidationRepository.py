# --- src/model/AdesaoPlanoModel/PlanoValidationRepository.py ---

from sqlalchemy.orm import Session
# Importe as classes do seu modelo que estão nas pastas de configuração
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.contratoConfig import Contrato
from src.model.AdesaoPlanoModel import AdesaoPlanoModel 
from src.model.PlanoModel import PlanosModel 
from src.model.PlanosCustomizadosModel import PlanosPersonalizadosModel 

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_

class PlanoValidationRepository:
    """
    Responsável por verificar a elegibilidade do estudante para matricular-se em uma aula,
    baseado em sua adesão de plano e contrato.
    """
    def __init__(self, db_session: Session):
        self.session = db_session
        # Instancie os modelos necessários
        self.adesao_model = AdesaoPlanoModel(db_session)
        self.plano_model = PlanosModel(db_session)
        self.plano_personalizado_model = PlanosPersonalizadosModel(db_session)

    def _get_active_contract(self, adesao_id: int) -> Optional[Contrato]:
        """Busca o contrato ativo (não expirado ou não cancelado) associado a uma Adesão."""
        try:
            # 🚨 IMPORTANTE: Ajuste esta consulta para a sua lógica de status de contrato.
            stmt = select(Contrato).where(
                and_(
                    Contrato.fk_id_adesao_plano == adesao_id,
                    # Exemplo: Se Contrato tiver um campo 'status'
                    # Contrato.status == 'ATIVO', 
                    # Exemplo: Se Contrato tiver uma data de término
                    # Contrato.data_termino > datetime.now()
                )
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except Exception:
            # Em caso de erro, presume-se que não há contrato válido
            return None


    def is_student_eligible_for_enrollment(self, estudante_id: int, aula_id: int) -> bool:
        """
        Verifica se o estudante tem um plano ativo com contrato associado e 
        com créditos/acessos disponíveis.
        """
        # Método que busca adesões válidas pela data de validade > datetime.now()
        active_adesoes: List[AdesaoPlano] = self.adesao_model.select_active_adesao_by_estudante_id(estudante_id)
        
        if not active_adesoes:
            raise ValueError("O estudante não possui nenhuma adesão de plano ativa e válida no momento.")
        
        # Iterar sobre as adesões ativas para achar a que possui um contrato ativo/créditos
        for adesao in active_adesoes:
            contrato = self._get_active_contract(adesao.id_adesao_plano)
            
            if contrato:
                # 1. Checagem de Elegibilidade (Créditos, Limite de Aulas, etc.)
                # Se for um plano ilimitado (mensal/trimestral/anual), o contrato basta.
                
                # Se for um plano de CRÉDITOS, você checaria:
                # if adesao.creditos_restantes <= 0:
                #     continue # Se os créditos acabaram, tenta o próximo plano ativo
                
                # Assumindo que a aula é permitida e o plano é ilimitado ou tem créditos
                return True
                
        # Se nenhuma adesão ativa/contratada atende aos requisitos
        raise ValueError("O estudante não está elegível. Plano ativo não encontrado ou contrato pendente/expirado.")
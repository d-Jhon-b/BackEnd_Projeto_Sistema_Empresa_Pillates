from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Optional

from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.model.PlanoModel import PlanosModel # Assumindo que você tem um Model para buscar planos
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, SubscribePlano
from src.model.userModel.typeUser.aluno import Estudante # Para validação de FK Estudante
from src.controllers.validations.permissionValidation import UserValidation

class AdesaoPlanoController:

    def subscribe_plano(self, session_db: Session, data_payload: SubscribePlanoPayload, current_user: Dict[str, Any]) -> SubscribePlano:
        UserValidation._check_aluno_or_admin_permission(current_user=current_user)
        
        fk_id_estudante = data_payload.fk_id_estudante
        plano_data = data_payload.fk_id_plano_Geral
        
        fk_id_plano = plano_data.fk_id_plano
        fk_id_plano_personalizado = plano_data.fk_id_plano_personalizado

        estudante_check = session_db.get(Estudante, fk_id_estudante)
        if not estudante_check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Estudante com ID {fk_id_estudante} não encontrado.")

        
        adesao_plano_model = PlanosModel(session_db) 
        
        if fk_id_plano:
            plano_obj = adesao_plano_model.select_plano_by_id(fk_id_plano)
            if not plano_obj:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Padrão com ID {fk_id_plano} não encontrado.")
            tipo_plano = plano_obj.tipo_plano.value
        else: 
            tipo_plano = 'mensal' 

        data_adesao = datetime.now()

        if tipo_plano == 'mensal':
            data_validade_calc = data_adesao + relativedelta(months=1)
        elif tipo_plano == 'trimestral':
            data_validade_calc = data_adesao + relativedelta(months=3)
        elif tipo_plano == 'semestral':
            data_validade_calc = data_adesao + relativedelta(months=6)
        elif tipo_plano == 'anual':
            data_validade_calc = data_adesao + relativedelta(months=12)
        else:
            data_validade_calc = data_adesao + relativedelta(months=1)

        dados_para_model = {
            "fk_id_estudante": fk_id_estudante,
            "fk_id_plano": fk_id_plano,
            "fk_id_plano_personalizado": fk_id_plano_personalizado,
            "data_validade": data_validade_calc
        }

        try:
            adesao_repo = AdesaoPlanoModel(session_db=session_db)
            new_adesao = adesao_repo.subscribe_plan(dados_para_model)
            
            if new_adesao is None:
                 raise Exception("Falha na persistência no banco de dados.")

            return SubscribePlano.model_validate(new_adesao)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro no serviço de adesão: {e}"
            )
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Optional

from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.model.PlanoModel import PlanosModel 
from src.model.AlunoModel import AlunoModel
from src.model.PlanosCustomizadosModel import PlanosPersonalizadosModel
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, SubscribePlano
from src.model.userModel.typeUser.aluno import Estudante # Para validação de FK Estudante
from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.validations.AdesaoValidation import AdesaoValidation

class AdesaoPlanoController:

    def subscribe_plano(self, session_db: Session, data_payload: SubscribePlanoPayload, current_user: Dict[str, Any]) -> SubscribePlano:
        UserValidation._check_aluno_or_admin_permission(current_user=current_user)

        adesao_repo = AdesaoPlanoModel(session_db=session_db) 
        adesao_plano_model = PlanosModel(session_db) 
        adesao_plano_personalizados_model = PlanosPersonalizadosModel(session_db) 

        fk_id_estudante = data_payload.fk_id_estudante
        plano_data = data_payload.fk_id_plano_Geral
        
        fk_id_plano = plano_data.fk_id_plano
        fk_id_plano_personalizado = plano_data.fk_id_plano_personalizado

        estudante_check = session_db.get(Estudante, fk_id_estudante)

        data_validade_calc: Optional[datetime] = None 
        tipo_plano: Optional[str] = None 
        data_adesao = datetime.now()

        if not estudante_check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Estudante com ID {fk_id_estudante} não encontrado.")

        if fk_id_plano:
            plano_obj = adesao_plano_model.select_plano_by_id(fk_id_plano)
            if not plano_obj:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Padrão com ID {fk_id_plano} não encontrado.")
            tipo_plano = plano_obj.tipo_plano

        elif fk_id_plano_personalizado:
            plano_obj = adesao_plano_personalizados_model.select_plano_by_id(fk_id_plano_personalizado)
            if not plano_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Personalizado com ID {fk_id_plano_personalizado} não encontrado.")
            
            if plano_obj.is_temporario and plano_obj.data_validade:
                data_validade_calc = plano_obj.data_validade

            tipo_plano = plano_obj.tipo_plano_livre

        data_adesao = datetime.now()
        AdesaoValidation._check_no_active_contract(session_db=session_db, estudante_id=fk_id_estudante)
        adesao_pendente = adesao_repo.select_pending_adesao_by_estudante(estudante_id=fk_id_estudante)
        
        if adesao_pendente is not None:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"O estudante ID {fk_id_estudante} já possui uma adesão pendente de contratação (ID: {adesao_pendente.id_adesao_plano}) que não expirou. Contrate-a ou aguarde sua expiração."
            )

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
            new_adesao = adesao_repo.subscribe_plan(dados_para_model)
            
            if new_adesao is None:
                 raise Exception("Falha na persistência no banco de dados.")

            return SubscribePlano.model_validate(new_adesao)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro no serviço de adesão: {e}"
            )
        


    def get_adesao_pendente_by_estudante(self, session_db: Session, estudante_id: int, current_user: Dict[str, Any]) -> SubscribePlano:

        aluno_model = AlunoModel(session_db)
        fk_id_user=aluno_model.select_id_user_by_fk_id_estudante(estudante_id=estudante_id)
        print(f'{fk_id_user}\n\n\n\n')

        UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=fk_id_user)

        adesao_repo = AdesaoPlanoModel(session_db=session_db)
        adesao_pendente = adesao_repo.select_pending_adesao_by_estudante(estudante_id=estudante_id)
        
        if adesao_pendente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Nenhuma adesão de plano pendente de contratação encontrada para o estudante ID {estudante_id}."
            )
        
        return SubscribePlano.model_validate(adesao_pendente)
    

    def get_all_adesoes_by_estudante(self, session_db: Session, estudante_id: int, current_user: Dict[str, Any]) -> list[SubscribePlano]:
        aluno_model = AlunoModel(session_db)
        fk_id_user = aluno_model.select_id_user_by_fk_id_estudante(estudante_id=estudante_id)

        if fk_id_user is None:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Estudante com ID {estudante_id} não encontrado.")
        
        UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=fk_id_user) 
        
        adesao_repo = AdesaoPlanoModel(session_db=session_db)
        todas_adesoes = adesao_repo.select_all_adesoes_by_estudante(estudante_id=estudante_id)
        
        return [SubscribePlano.model_validate(adesao) for adesao in todas_adesoes]
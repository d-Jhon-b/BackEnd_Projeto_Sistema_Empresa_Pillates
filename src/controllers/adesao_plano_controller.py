from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Optional

from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.model.PlanoModel import PlanosModel 
from src.model.AlunoModel import AlunoModel
from src.model.PlanosCustomizadosModel import PlanosPersonalizadosModel
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, SubscribePlano,AdesaoPlanoBase,AdesaoPlanoUpdate
from src.model.userModel.typeUser.aluno import Estudante # Para validação de FK Estudante
from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.validations.AdesaoValidation import AdesaoValidation
from src.controllers.utils.date_calculators import ValidityCalculator

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
        
        is_personalizado = False
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
        
        
        ##  |
        #   v
        is_personalizado = fk_id_plano is None and fk_id_plano_personalizado is not None

        if tipo_plano:
            data_validade_calc = ValidityCalculator.calculate_validity_date(
                tipo_plano=tipo_plano,
                is_personalizado=is_personalizado,
                plano_obj=plano_obj,
                start_date=data_adesao # 👈 Data de início injetada
            )
        else:
             # Fallback caso plano_obj não tenha tipo (deve ser tratado como erro 404 antes)
            data_validade_calc = data_adesao + relativedelta(months=1)
        # if tipo_plano == 'mensal':
        #     data_validade_calc = data_adesao + relativedelta(months=1)
        # elif tipo_plano == 'trimestral':
        #     data_validade_calc = data_adesao + relativedelta(months=3)
        # elif tipo_plano == 'semestral':
        #     data_validade_calc = data_adesao + relativedelta(months=6)
        # elif tipo_plano == 'anual':
        #     data_validade_calc = data_adesao + relativedelta(months=12)
        # else:
        #     data_validade_calc = data_adesao + relativedelta(months=1)

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
    
    def get_adesao_by_id(self, session_db: Session, adesao_id: int, current_user: Dict[str, Any]) -> SubscribePlano:
        UserValidation._check_admin_permission(current_user=current_user)
        
        adesao_repo = AdesaoPlanoModel(session_db=session_db)
        
        adesao = adesao_repo.select_adesao_by_id(adesao_id)
        
        if not adesao:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Adesão com ID {adesao_id} não encontrada.")
                    
        return SubscribePlano.model_validate(adesao)





    def update_adesao_plano_data(self, session_db: Session, adesao_id: int, data_update: AdesaoPlanoUpdate, current_user: Dict[str, Any]) -> SubscribePlano:
        UserValidation._check_admin_permission(current_user=current_user)
        update_dict = data_update.model_dump(exclude_unset=True)

        adesao_repo = AdesaoPlanoModel(session_db=session_db)
        plano_model = PlanosModel(session_db) 
        plano_personalizado_model = PlanosPersonalizadosModel(session_db) 

        is_plano_changed = ('fk_id_plano' in update_dict or 'fk_id_plano_personalizado' in update_dict)
        is_data_validade_explicit = ('data_validade' in update_dict)

        if is_plano_changed and not is_data_validade_explicit:
            
            start_date_for_recalculation = datetime.now() 

            fk_id_plano = update_dict.get('fk_id_plano')
            fk_id_plano_personalizado = update_dict.get('fk_id_plano_personalizado')

            plano_obj = None
            is_personalizado = False
            tipo_plano = None

            if fk_id_plano and fk_id_plano_personalizado:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido alterar para Plano Padrão e Personalizado simultaneamente.")

            if fk_id_plano:
                plano_obj = plano_model.select_plano_by_id(fk_id_plano)
                if not plano_obj:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Padrão com ID {fk_id_plano} não encontrado.")
                tipo_plano = plano_obj.tipo_plano

            elif fk_id_plano_personalizado:
                is_personalizado = True
                plano_obj = plano_personalizado_model.select_plano_by_id(fk_id_plano_personalizado)
                if not plano_obj:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Personalizado com ID {fk_id_plano_personalizado} não encontrado.")
                tipo_plano = plano_obj.tipo_plano_livre

            if tipo_plano:
                update_dict['data_validade'] = ValidityCalculator.calculate_validity_date(
                    tipo_plano=tipo_plano,
                    is_personalizado=is_personalizado,
                    plano_obj=plano_obj,
                    start_date=start_date_for_recalculation # 👈 Data de início injetada
                )
            else:
                update_dict['data_validade'] = start_date_for_recalculation + relativedelta(months=1)


        if not update_dict:
            adesao = adesao_repo.select_adesao_by_id(adesao_id)
            if not adesao:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Adesão com ID {adesao_id} não encontrada.")
            return SubscribePlano.model_validate(adesao)
            
        try:
            updated_adesao = adesao_repo.update_adesao_plano(adesao_id, update_dict)
            
            if updated_adesao is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Adesão com ID {adesao_id} não encontrada para atualização.")
            return SubscribePlano.model_validate(updated_adesao)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro ao atualizar Adesão {adesao_id}: {e}"
            )
        

    
        
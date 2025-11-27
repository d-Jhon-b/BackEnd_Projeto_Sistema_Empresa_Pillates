from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any


from src.controllers.plano_controller import PlanosController 
from src.controllers.plano_personalizado_controller import PlanosPersonalizadosController

from src.schemas.plano_schemas import PlanoResponse
from src.schemas.planos_personalizados_schemas import PlanoPersonalizadoResponse
from src.controllers.validations.permissionValidation import UserValidation

from src.model.planosModel import adesaoPlanoConfig, planosPersonalizadosConfig


class ConsultaPlanosGeralController:
    def __init__(self):
        self.plano_padrao_controller = PlanosController()
        self.plano_personalizado_controller = PlanosPersonalizadosController()

    def get_all_planos_geral(self, session_db: Session, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:        
        UserValidation._check_all_permission(current_user) 
        
        try:
            planos_padrao = self.plano_padrao_controller.get_all_planos_padrao(
                session_db=session_db, 
                current_user=current_user
            )
            
            planos_personalizados = self.plano_personalizado_controller.get_all_planos_personalizados(
                session_db=session_db, 
                current_user=current_user
            )
            todos_planos = []
            
            for plano in planos_padrao:
                plano_dict = PlanoResponse.model_validate(plano).model_dump()
                plano_dict['tipo_plano'] = 'padrao'
                todos_planos.append(plano_dict)
                
            for plano in planos_personalizados:
                plano_dict = PlanoPersonalizadoResponse.model_validate(plano).model_dump()
                plano_dict['tipo_plano'] = 'personalizado'
                todos_planos.append(plano_dict)
            
            return todos_planos
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha ao buscar todos os Planos: {e}"
            )
        
    def get_plano_atual(self, session_db: Session, current_user: Dict[str, Any]) -> Dict[str, Any]:
        try:
            aluno_id = current_user["id"]

            plano_padrao = session_db.execute( 
                select(adesaoPlanoConfig)
                .where(adesaoPlanoConfig.fk_id_estudante == aluno_id)
                .order_by(adesaoPlanoConfig.id.desc())
            ).scalars().first()

            plano_personalizado = session_db.execute(
                select(planosPersonalizadosConfig)
                .where(planosPersonalizadosConfig.fk_id_estudante == aluno_id)
                .order_by(planosPersonalizadosConfig.id.desc())
            ).scalars().first()

            plano_atual = plano_personalizado or plano_padrao

            if not plano_atual:
                return {"message": "O aluno não possui plano ativo."}

            return {
                "adesao_id": plano_atual.id,
                "plano_id": plano_atual.fk_id_plano,
                "nome_plano": plano_atual.plano_nome,
                "valor": plano_atual.valor,
                "data_adesao": plano_atual.data_adesao,
                "tipo": "personalizado" if plano_personalizado else "padrao",
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha ao buscar o plano atual: {e}"
            )
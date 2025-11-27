from sqlalchemy.orm import Session
from sqlalchemy import exc
from dateutil.relativedelta import relativedelta
from datetime import datetime
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano 
from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.model.planosModel.contratoConfig import Contrato 
from src.model.ContratoModel import ContratoModel 

from src.services.pagamentosService import PagamentoService
# from src.model.planosModel.planoConfig import Planos
from src.model.PlanoModel import PlanosModel 
from src.model.PlanosCustomizadosModel import PlanosPersonalizadosModel 
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload,AdesaoPlanoBase, AdesaoPlanoUpdate
import logging
from fastapi import HTTPException,status
from typing import Dict, Optional, List, Any

class AdesaoContratoService:

    def __init__(self, db_session: Session):
        self.session = db_session
        self.plano_model = PlanosModel(db_session)
        self.plano_personalizado_model = PlanosPersonalizadosModel(db_session)
        self.adesao_model = AdesaoPlanoModel(db_session)
        self.contrato_model = ContratoModel(db_session)
        self.pagamento_service = PagamentoService(db_session)
    
    def _calculate_validity(self, plano_type: str, data_adesao: datetime) -> datetime:

        if plano_type == 'mensal':
            return data_adesao + relativedelta(months=1)
        elif plano_type == 'trimestral':
            return data_adesao + relativedelta(months=3)
        else:
            return data_adesao + relativedelta(months=1) 


    def create_adesao_and_contract(self, data: SubscribePlanoPayload, estudante_id: int, current_user:Dict[str, Any]) -> Dict[str, Any]:
        
        plano_geral = data.fk_id_plano_Geral
        fk_id_plano = plano_geral.fk_id_plano
        fk_id_plano_personalizado = plano_geral.fk_id_plano_personalizado

        plano_details: Optional[Any] = None
        tipo_plano_calc: str
        qtde_aulas_totais: int
        
        if fk_id_plano:
            plano_details = self.plano_model.select_plano_by_id(fk_id_plano)
            if plano_details:
                tipo_plano_calc = plano_details.tipo_plano
                qtde_aulas_totais = plano_details.qtde_aulas_totais
        elif fk_id_plano_personalizado:
            plano_details = self.plano_personalizado_model.select_plano_by_id(fk_id_plano_personalizado)
            if plano_details:
                tipo_plano_calc = plano_details.tipo_plano_livre 
                qtde_aulas_totais = plano_details.qtde_aulas_totais
        
        if not plano_details:
            plano_id_erro = fk_id_plano if fk_id_plano else fk_id_plano_personalizado
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Plano selecionado (ID: {plano_id_erro}) não encontrado."
            )
            
        data_adesao = datetime.now() 
        data_termino_contrato = self._calculate_validity(tipo_plano_calc, data_adesao)
        
        try:
            nova_adesao = AdesaoPlano(
                fk_id_estudante=estudante_id,
                fk_id_plano=fk_id_plano, 
                fk_id_plano_personalizado=fk_id_plano_personalizado, 
                data_adesao=data_adesao,
                data_validade=data_termino_contrato 
            )
            self.session.add(nova_adesao)
            self.session.flush() 

            novo_contrato = Contrato(
                fk_id_estudante=estudante_id,
                fk_id_plano=fk_id_plano, 
                fk_id_plano_personalizado=fk_id_plano_personalizado,
                fk_id_adesao_plano=nova_adesao.id_adesao_plano, 
                valor_final=plano_details.valor_plano,
                data_inicio=data_adesao,
                data_termino=data_termino_contrato,
                aulas_restantes=qtde_aulas_totais,
                status_contrato='ativo' 
            )
            self.session.add(novo_contrato)
            self.session.flush()
            parcelas_geradas = self.pagamento_service.gerar_pagamentos_contrato(
                contrato=novo_contrato, 
                current_user=current_user
            )
            
            self.session.commit()
            self.session.refresh(nova_adesao)
            self.session.refresh(novo_contrato)
            
            return {
                "adesao": nova_adesao, 
                "contrato": novo_contrato,
                "parcelas": parcelas_geradas 
            }

        except exc.SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"Erro transacional ao criar adesão e contrato: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao concluir a transação de adesão e contrato devido a um erro de banco de dados.")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro inesperado: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor.")

    def delete_adesao_and_contract(self, adesao_id: int, current_user: Dict[str, Any]) -> bool:
        # UserValidation._check_admin_permission(current_user) 
        
        try:
            adesao_db = self.adesao_model.select_adesao_by_id(adesao_id)
            if not adesao_db:
                return False 
            
            contrato_db = self.contrato_model.select_contrato_by_adesao(adesao_id) 
            
            if contrato_db:
                success_contrato = self.contrato_model.delete_contrato_by_id(contrato_db.id_contrato)
                
                if not success_contrato:
                    raise Exception(f"Falha ao excluir Contrato ID {contrato_db.id_contrato} associado à Adesão.")
                
            success_adesao = self.adesao_model.delete_adesao_by_id(adesao_id)
            
            if not success_adesao:
                raise Exception(f"Falha ao excluir Adesão ID {adesao_id}")

            self.session.commit()
            return True
        
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro transacional ao deletar adesão e contrato: {e}")
            if str(e).startswith("Falha ao excluir"):
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro de consistência ao tentar excluir: {e}")
            else:
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao concluir a exclusão transacional devido a um erro interno.")



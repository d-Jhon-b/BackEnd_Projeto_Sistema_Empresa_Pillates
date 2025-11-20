from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados

from src.model.planosModel.contratoConfig import Contrato


#teste de planos
from src.database.connPostGreNeon import CreateSessionPostGre
from src.schemas.adesao_plano_schemas import SubscribePlano, SubscribePlanoPayload

from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound
from sqlalchemy.orm import Session, joinedload, join
from sqlalchemy import select, and_
# from sqlalchemy import join
from typing import Dict, Optional, Union, Any
import logging
from datetime import datetime

class AdesaoPlanoModel():
    def  __init__(self, session_db:Session):
        self.session = session_db

    def select_pending_adesao_by_estudante(self, estudante_id: int) -> Optional[AdesaoPlano]:
        try:
            current_time = datetime.now()
            has_contract_stmt = select(Contrato.id_contrato).where(
                Contrato.fk_id_adesao_plano == AdesaoPlano.id_adesao_plano
            ).exists()
            
            stmt = (
                select(AdesaoPlano)
                .where(
                    and_(
                        AdesaoPlano.fk_id_estudante == estudante_id,
                        AdesaoPlano.data_validade > current_time,
                        ~has_contract_stmt  
                    )
                )
                .order_by(AdesaoPlano.data_adesao.desc()) 
            )

            return self.session.execute(stmt).scalar_one_or_none()
            
        except MultipleResultsFound as err:
            logging.error(f"Múltiplas adesões pendentes encontradas para o estudante {estudante_id}. {err}")
            return None 
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar adesão pendente do estudante {estudante_id}: {err}")
            return None

    def subscribe_plan(self, data_to_insert: Dict[str, Any]) -> Optional[AdesaoPlano]:
        try:
            # print(f'\n\n\n{data_to_insert}\n\n\n')
            # fk_id_estudante = data_to_insert.get('fk_id_estudante')
            # fk_plano_geral = data_to_insert.get('fk_id_plano_Geral', {})
            # plano_data = {
            #     'fk_id_estudante': fk_id_estudante,
            #     'fk_id_plano': fk_plano_geral.get('fk_id_plano'),
            #     'fk_id_plano_personalizado': fk_plano_geral.get('fk_id_plano_personalizado'),
            #     'data_validade': data_to_insert.get('data_validade') 
            # }            
            # plano_data = {k: v for k, v in plano_data.items() if v is not None}
                        
            # new_subscribe = AdesaoPlano(**plano_data)
            
            # self.session.add(new_subscribe)
            # self.session.commit()
            # self.session.refresh(new_subscribe)
            # return new_subscribe
        
            new_subscribe = AdesaoPlano(**data_to_insert)            
            self.session.add(new_subscribe)
            self.session.commit()
            self.session.refresh(new_subscribe)
            return new_subscribe
        
        except SQLAlchemyError as err:
            logging.error(f'{err}')
            self.session.rollback()
            return None
        except SQLAlchemyError as err:
            logging.error(f'{err}')
            self.session.rollback()
            return None
        

    def update_adesao_plano(self, id_adesao_plano: int, data_to_update: Dict[str, Any]) -> Optional[AdesaoPlano]:
        if not data_to_update:
            return self.session.get(AdesaoPlano, id_adesao_plano)
            
        update_dict = {k: v for k, v in data_to_update.items() if v is not None}
        
        try:
            existing_adesao = self.session.get(AdesaoPlano, id_adesao_plano)
            if not existing_adesao:
                return None
            
            for key, value in update_dict.items():
                setattr(existing_adesao, key, value)
            
            self.session.commit()
            self.session.refresh(existing_adesao)
            return existing_adesao
            
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao atualizar adesão {id_adesao_plano}: {err}")
            self.session.rollback()
            return None
        except Exception as err:
            logging.error(f"Erro inesperado ao atualizar adesão {id_adesao_plano}: {err}")
            self.session.rollback()
            return None

    def select_active_adesao_by_estudante_id(self, estudante_id: int) -> list[AdesaoPlano]:

        try:
            current_time = datetime.now()
            
            stmt = (
                select(AdesaoPlano)
                .where(
                    and_(
                        AdesaoPlano.fk_id_estudante == estudante_id,
                        AdesaoPlano.data_validade > current_time
                    )
                )
            )
            
            active_adesoes = self.session.scalars(stmt).all()
            return active_adesoes
            
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar adesões ativas do estudante {estudante_id}: {err}")
            return []
        except Exception as err:
            logging.error(f"Erro inesperado ao buscar adesões ativas: {err}")
            return []
    
    def select_adesao_by_id(self, adesao_id: int) -> Optional[AdesaoPlano]:
        try:
            stmt = select(AdesaoPlano).where(AdesaoPlano.id_adesao_plano == adesao_id)
            # adesao_db = self.session.get(AdesaoPlano, adesao_id)
            adesao_db=self.session.execute(stmt).unique().scalar_one_or_none()
            return adesao_db
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar adesão {adesao_id}: {err}")
            return None
        except Exception as err:
            logging.error(f"Erro inesperado ao buscar adesão {adesao_id}: {err}")
            return None

    def _get_contrato_by_adesao_id(self, adesao_id: int) -> Optional[Contrato]:
        try:
            stmt = select(Contrato).where(Contrato.fk_id_adesao_plano == adesao_id)
            contrato_db = self.session.execute(stmt).unique().scalar_one_or_none()
            return contrato_db
            
        except Exception as err:
            logging.error(f"Erro ao buscar contrato para adesão {adesao_id}: {err}")
            return None

    def select_all_adesoes_by_estudante(self, estudante_id: int) -> list[AdesaoPlano]:
        try:
            stmt = (
                select(AdesaoPlano)
                .where(AdesaoPlano.fk_id_estudante == estudante_id)
                .order_by(AdesaoPlano.data_adesao.desc()) 
            )
            return self.session.scalars(stmt).all()
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar todas as adesões do estudante {estudante_id}: {err}")
            return []
    




# from datetime import datetime
# from dateutil.relativedelta import relativedelta

# create_session = CreateSessionPostGre()
# session: Session = create_session.get_session()
# adesao_repo = AdesaoPlanoModel(session_db=session)

# FK_ID_PLANO_TESTE=1
# FK_ID_ESTUDANTE = 1 
# DATA_ADESAO = datetime.now().replace(microsecond=0)
# # A validade para um plano mensal (tipo_plano=MENSAL) é de 1 mês
# DATA_VALIDADE = DATA_ADESAO + relativedelta(months=1)

# if FK_ID_PLANO_TESTE:
#     # Este é o dicionário LIMPO que o Controller deve gerar (como refatoramos)
#     adesao_data_plana = {
#         "fk_id_estudante": FK_ID_ESTUDANTE,
#         "fk_id_plano": FK_ID_PLANO_TESTE,
#         "fk_id_plano_personalizado": None, # Importante: apenas um dos dois deve ser preenchido
#         "data_adesao": DATA_ADESAO,
#         "data_validade": DATA_VALIDADE
#     }

#     try:
#         new_adesao = adesao_repo.subscribe_plan(adesao_data_plana)
        
#         if new_adesao:
#             FK_ID_ADESAO_TESTE = new_adesao.id_adesao_plano
#             print(f" SUCESSO! Adesão criada. ID: {FK_ID_ADESAO_TESTE}")
#             print(f"   Validade: {new_adesao.data_validade.strftime('%Y-%m-%d')}")
#         else:
#             FK_ID_ADESAO_TESTE = None
#             print(" FALHA ao criar Adesão.")

#     except Exception as e:
#         print(f" ERRO no Teste Adesão: {e}")
#         FK_ID_ADESAO_TESTE = None
# else:
#     print(" Pulando Adesão: Plano Padrão não foi criado.")
#     FK_ID_ADESAO_TESTE = None
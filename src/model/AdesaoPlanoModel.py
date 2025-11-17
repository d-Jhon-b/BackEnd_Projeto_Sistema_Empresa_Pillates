from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados

from src.model.planosModel.contratoConfig import Contrato


#teste de planos
from src.database.connPostGreNeon import CreateSessionPostGre
from src.schemas.adesao_plano_schemas import SubscribePlano, SubscribePlanoPayload

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, join
# from sqlalchemy import join
from typing import Dict, Optional, Union, Any
import logging

class AdesaoPlanoModel():
    def  __init__(self, session_db:Session):
        self.session = session_db


    def subscribe_plan(self, data_to_insert: Dict[str, Any]) -> Optional[AdesaoPlano]:
        try:
            print(f'\n\n\n{data_to_insert}\n\n\n')
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
        



from datetime import datetime
from dateutil.relativedelta import relativedelta

create_session = CreateSessionPostGre()
session: Session = create_session.get_session()
adesao_repo = AdesaoPlanoModel(session_db=session)
FK_ID_ESTUDANTE = 1 


data_adesao = datetime.now()


# FK_ID_PLANO_PADRAO = 1
# data_validade_mensal = data_adesao + relativedelta(months=1)

# dados_plano_padrao: Dict[str, Any] = {
#     "fk_id_estudante": FK_ID_ESTUDANTE,
#     "fk_id_plano": FK_ID_PLANO_PADRAO,
#     "fk_id_plano_personalizado": None, 
#     "data_validade": data_validade_mensal
# }

# try:
#     # print(dados_plano_padrao)
#     new_adesao_padrao = adesao_repo.subscribe_plan(dados_plano_padrao)
#     if new_adesao_padrao:
#         print(f"ID Adesão: {new_adesao_padrao.id_adesao_plano}")
#         response_schema = SubscribePlano.model_validate(new_adesao_padrao)
#         print(f"  FK Plano Padrão: {response_schema.fk_id_plano}")
#         print(f"  Data Validade: {response_schema.data_validade.strftime('%Y-%m-%d %H:%M')}")
#     else:
#         print(" FALHA na inserção do Plano Padrão.")
        
# except SQLAlchemyError as e:
#     print(f"ERRO DB no Teste 1: {e}")
#     session.rollback()
# except Exception as e:
#     print(f"  ERRO INESPERADO no Teste 1: {e}")




# FK_ID_PLANO_PERSONALIZADO = 1  
# data_validade_trimestral = data_adesao + relativedelta(months=3)

# dados_plano_personalizado: Dict[str, Any] = {
#     "fk_id_estudante": FK_ID_ESTUDANTE,
#     "fk_id_plano": None, 
#     "fk_id_plano_personalizado": FK_ID_PLANO_PERSONALIZADO, 
#     "data_validade": data_validade_trimestral
# }

# try:
#     new_adesao_personalizado = adesao_repo.subscribe_plan(dados_plano_personalizado)
    
#     if new_adesao_personalizado:
#         print(f" ID Adesão: {new_adesao_personalizado.id_adesao_plano}")
#         response_schema = SubscribePlano.model_validate(new_adesao_personalizado)
#         print(f"FK Plano Personalizado: {response_schema.fk_id_plano_personalizado}")
#         print(f"Data Validade: {response_schema.data_validade.strftime('%Y-%m-%d %H:%M')}")
#     else:
#         print("FALHA na inserção do Plano Personalizado.")
        
# except SQLAlchemyError as e:
#     print(f"ERRO DB no Teste 2: {e}")
#     session.rollback()
# except Exception as e:
#     print(f"ERRO INESPERADO no Teste 2: {e}")
from src.model.planosModel.contratoConfig import Contrato
from src.model.UserModel import Usuario
from src.model.userModel.typeUser.aluno import Estudante
# from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
# from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
# from src.model.planosModel.planoConfig import Planos


import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class ContratoModel():
    def __init__(self, session_db: Session):
        self.session = session_db

    def create_contract(self, data_to_insert: Dict[str, Any]) -> Optional[Contrato]:
        try:
            new_contrato = Contrato(**data_to_insert)
            self.session.add(new_contrato)
            self.session.commit()
            self.session.refresh(new_contrato)
            return new_contrato
            
        except SQLAlchemyError as err:
            logging.error(f"Erro de Banco de Dados ao criar Contrato: {err}")
            self.session.rollback()
            return None
        






import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any

# Suas importações
from src.database.connPostGreNeon import CreateSessionPostGre 
from src.schemas.contrato_schemas import ContratoResponse, StatusContratoEnum 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


create_session = CreateSessionPostGre()
session: Session = create_session.get_session()

contrato_repo = ContratoModel(session_db=session)
FK_ID_ESTUDANTE = 1 
FK_ID_ADESAO_PLANO = 8
DATA_INICIO = datetime.now().replace(microsecond=0)
DATA_TERMINO_PADRAO = DATA_INICIO + timedelta(days=30)
DATA_TERMINO_PERSONALIZADO = DATA_INICIO + timedelta(days=90)
print("\n[TESTE 1] Criação de Contrato com Plano Padrão (ID=1)")

FK_ID_PLANO_PADRAO = 1

dados_plano_padrao: Dict[str, Any] = {
    "fk_id_estudante": FK_ID_ESTUDANTE,
    "fk_id_adesao_plano": FK_ID_ADESAO_PLANO,
    "fk_id_plano": FK_ID_PLANO_PADRAO,
    "fk_id_plano_personalizado": None, 
    "data_inicio": DATA_INICIO,
    "data_termino": DATA_TERMINO_PADRAO,
    "status_contrato": StatusContratoEnum.ATIVO.value 
}

try:
    new_contrato_padrao = contrato_repo.create_contract(dados_plano_padrao)
    
    if new_contrato_padrao:
        print(f"SUCESSO! ID Contrato: {new_contrato_padrao.id_contrato}")
        
        response_schema = ContratoResponse.model_validate(new_contrato_padrao)
    else:
        print("FALHA na inserção do Contrato Padrão.")
        
except SQLAlchemyError as e:
    print(f"Err no Teste 1: {e}")
    session.rollback()
except Exception as e:
    print(f" Err isnesperado no Teste 1: {e}")

# print("\n[TESTE 2] Criação de Contrato com Plano Personalizado (ID=2)")
# FK_ID_PLANO_PERSONALIZADO = 1
# dados_plano_personalizado: Dict[str, Any] = {
#     "fk_id_estudante": FK_ID_ESTUDANTE,
#     "fk_id_adesao_plano": FK_ID_ADESAO_PLANO,
#     "fk_id_plano": None, 
#     "fk_id_plano_personalizado": FK_ID_PLANO_PERSONALIZADO, 
#     "data_inicio": DATA_INICIO,
#     "data_termino": DATA_TERMINO_PERSONALIZADO,
#     "status_contrato": StatusContratoEnum.ATIVO.value
# }

# try:
#     new_contrato_personalizado = contrato_repo.create_contract(dados_plano_personalizado)
    
#     if new_contrato_personalizado:
#         print(f"SUCESSO! ID Contrato: {new_contrato_personalizado.id_contrato}")
        
#         response_schema = ContratoResponse.model_validate(new_contrato_personalizado)

#     else:
#         print("FALHA na inserção do Contrato Personalizado.")
        
# except SQLAlchemyError as e:
#     print(f"ERRO DB no Teste 2: {e}")
#     session.rollback()
# except Exception as e:
#     print(f" ERRO INESPERADO no Teste 2: {e}")

session.close()

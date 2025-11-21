from src.model.financasModel.pagamentoConfig import Pagamento
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.model.planosModel.planoConfig import Planos
from src.model.userModel.typeUser.aluno import Estudante
from src.model.userModel.userConfig import Usuario

from src.model.financasModel.vendaExtraConfig import VendaExtra # Não precisa ser importado aqui se não for usado
from src.model.planosModel.contratoConfig import Contrato # Não precisa ser importado aqui se não for usado

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError

from typing import Dict, Any, Optional, List
import logging


class PagamentoModel(): 
    def __init__(self, session_db: Session):
        self.session = session_db

    # def select_payment_by_id(self, id_pagamento: int) -> Optional[Pagamento]:
    #     try:
    #         stmt = select(Pagamento).where(Pagamento.id_pagamento == id_pagamento)
    #         # return self.session.get(Pagamento, id_pagamento)
    #         result_search=self.session.execute(stmt).unique().scalar_one_or_none()
    #         return result_search
    #     except SQLAlchemyError:
    #         return None
            
    def select_payments_by_contrato(self, id_contrato: int) -> List[Pagamento]:
        try:
            # print(id_contrato)
            stmt = select(Pagamento).where(Pagamento.fk_id_contrato == id_contrato).order_by(Pagamento.data_vencimento)
            results = self.session.execute(stmt).scalars().all()
            return results
        except SQLAlchemyError as err:
            logging.error(f'erro ao buscar dados no banco{err}')
            return []
        except Exception:
            logging.error(f'erro ao processar resultado{err}')
            return []
        
    def select_payment_by_estudante(self, id_estudante:int)->List[Pagamento]:
        try:
            stmt=select(Pagamento).where(Pagamento.fk_id_estudante == id_estudante)
            results = self.session.execute(stmt).scalars().all()
            return results
        except SQLAlchemyError as err:
            self.session.rollback()
            logging.error(f'erro ao processar resultado{err}')
            return []
        except Exception as err:
            self.session.rollback()
            logging.error(f'erro ao processar resultado{err}')
            return []
    



    # def create_payment(self, data_to_insert: Dict[str, Any]) -> Optional[Pagamento]:
    #     """Cria um novo registro de pagamento."""
    #     try:
    #         new_payment = Pagamento(**data_to_insert)
    #         self.session.add(new_payment)
    #         self.session.commit()
    #         self.session.refresh(new_payment)
    #         return new_payment
    #     except SQLAlchemyError as err:
    #         logging.error(f"Erro de DB ao criar Pagamento: {err}")
    #         self.session.rollback()
    #         return None

    

    # def update_payment_status(self, id_pagamento: int, new_status: str) -> Optional[Pagamento]:
    #     """Atualiza o status do pagamento (e a data de pagamento se for 'pago')."""
    #     update_data = {'status_pagamento': new_status}
    #     if new_status.lower() == 'pago':
    #         update_data['data_pagamento'] = func.now() # Usa a função do banco para a hora atual
            
    #     try:
    #         update_stmt = (
    #             update(Pagamento)
    #             .where(Pagamento.id_pagamento == id_pagamento)
    #             .values(**update_data)
    #         )
    #         result = self.session.execute(update_stmt)
            
    #         if result.rowcount == 0:
    #             self.session.rollback()
    #             return None
            
    #         self.session.commit()
    #         return self.session.get(Pagamento, id_pagamento)
    #     except SQLAlchemyError as err:
    #         logging.error(f"Erro de DB ao atualizar Pagamento {id_pagamento}: {err}")
    #         self.session.rollback()
    #         return None


# from src.database.connPostGreNeon import CreateSessionPostGre
# create_session = CreateSessionPostGre()
# session=create_session.get_session()

# try:
#     pagamento_model=PagamentoModel(session_db=session)
#     # id_contrato=3
#     # results = pagamento_model.select_payments_by_contrato(id_contrato=id_contrato)
#     # print(results)
#     # for i in results:
#     #     print(i)
    
#     id_pagamento=3
#     result_on_id = pagamento_model.select_payment_by_id(id_pagamento=id_pagamento)
#     print(result_on_id)
# except SQLAlchemyError as err:
#     print(err)
# except Exception as err:
#     print(err)


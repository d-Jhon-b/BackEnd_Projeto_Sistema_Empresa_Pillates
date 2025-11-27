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
    


from src.model.financasModel.vendaExtraConfig import VendaExtra
from src.model.financasModel.pagamentoConfig import Pagamento 


from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional, List
import logging


class VendaExtraModel():
    def __init__(self, session_db: Session):
        self.session = session_db

    def create_venda_extra(self, data_to_insert: Dict[str, Any]) -> Optional[VendaExtra]:
        """Cria um novo registro de venda extra."""
        try:
            new_venda = VendaExtra(**data_to_insert)
            self.session.add(new_venda)
            self.session.commit()
            self.session.refresh(new_venda)
            return new_venda
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao criar Venda Extra: {err}")
            self.session.rollback()
            return None
            
    def select_venda_by_id(self, id_venda_extra: int) -> Optional[VendaExtra]:
        """Busca uma venda extra pelo ID, carregando o pagamento associado."""
        try:
            stmt = (
                select(VendaExtra)
                .where(VendaExtra.id_venda_extra == id_venda_extra)
                .options(joinedload(VendaExtra.pagamento))
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar Venda Extra {id_venda_extra}: {err}")
            return None
 
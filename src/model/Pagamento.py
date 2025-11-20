from src.model.financasModel.pagamentoConfig import Pagamento
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

    def create_payment(self, data_to_insert: Dict[str, Any]) -> Optional[Pagamento]:
        """Cria um novo registro de pagamento."""
        try:
            new_payment = Pagamento(**data_to_insert)
            self.session.add(new_payment)
            self.session.commit()
            self.session.refresh(new_payment)
            return new_payment
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao criar Pagamento: {err}")
            self.session.rollback()
            return None

    def select_payment_by_id(self, id_pagamento: int) -> Optional[Pagamento]:
        """Busca um pagamento pelo ID."""
        try:
            return self.session.get(Pagamento, id_pagamento)
        except SQLAlchemyError:
            return None
            
    def select_payments_by_contrato(self, id_contrato: int) -> List[Pagamento]:
        """Busca todos os pagamentos associados a um contrato."""
        try:
            stmt = select(Pagamento).where(Pagamento.fk_id_contrato == id_contrato).order_by(Pagamento.data_vencimento)
            return self.session.execute(stmt).scalars().all()
        except SQLAlchemyError:
            return []

    def update_payment_status(self, id_pagamento: int, new_status: str) -> Optional[Pagamento]:
        """Atualiza o status do pagamento (e a data de pagamento se for 'pago')."""
        update_data = {'status_pagamento': new_status}
        if new_status.lower() == 'pago':
            update_data['data_pagamento'] = func.now() # Usa a função do banco para a hora atual
            
        try:
            update_stmt = (
                update(Pagamento)
                .where(Pagamento.id_pagamento == id_pagamento)
                .values(**update_data)
            )
            result = self.session.execute(update_stmt)
            
            if result.rowcount == 0:
                self.session.rollback()
                return None
            
            self.session.commit()
            return self.session.get(Pagamento, id_pagamento)
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao atualizar Pagamento {id_pagamento}: {err}")
            self.session.rollback()
            return None
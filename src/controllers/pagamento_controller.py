from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Dict, Any

from src.model.PagamentoModel import PagamentoModel

from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.utils.TargetUserFinder import TargetUserFinder
from src.controllers.utils.TargetUserFinder import TargetUserFinder
from src.schemas.pagamento_schemas import PagamentoBase, PagamentoInput, PagamentoResponse

import logging

class PagamentoController():

    def select_payment_by_estudante_controller(self, id_estudante, curent_user:Dict[str, Any],session_db:Session):
        try:
            target_user = TargetUserFinder.check_and_get_target_user_id(session_db=session_db,current_user=curent_user, estudante_id=id_estudante)

            print(target_user)
            if target_user is None:
                return None
            pagamento_model = PagamentoModel(session_db=session_db)
            pagamentos_results = pagamento_model.select_payment_by_estudante(id_estudante=id_estudante)
            if not pagamentos_results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nenhum resultado encontrado"
                )
            return [PagamentoResponse.model_validate(e) for e in pagamentos_results]
        
        except HTTPException as err:
            logging.error(f'Erro ao processar request:{err}')
            raise err
        except SQLAlchemyError as err:
            logging.error(f'Erro ao processar consulta:{err}')
            raise err
        except Exception as err:
            logging.error(f'Erro ao processar:{err}')
            raise err
        


    def select_payments_by_contrato_controller(self, id_contrato: int, current_user: Dict[str, Any], session_db: Session) -> List[PagamentoResponse]:
        try:
            pagamento_model = PagamentoModel(session_db=session_db)
            pagamentos_results = pagamento_model.select_payments_by_contrato(id_contrato=id_contrato)
            if not pagamentos_results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nenhum pagamento encontrado para o Contrato ID {id_contrato}."
                )

            primeiro_pagamento = pagamentos_results[0]
            TargetUserFinder.check_and_get_target_user_id(
                session_db=session_db,
                current_user=current_user,
                estudante_id=primeiro_pagamento.fk_id_estudante
            )
            
            return [PagamentoResponse.model_validate(p) for p in pagamentos_results]

        except HTTPException as err:
            logging.error(f'Erro ao processar request: {err.detail}')
            raise err
        except SQLAlchemyError as err:
            logging.error(f'Erro de DB ao processar consulta: {err}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao consultar pagamentos do contrato.")
        except Exception as err:
            logging.error(f'Erro inesperado: {err}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado.")
        

    
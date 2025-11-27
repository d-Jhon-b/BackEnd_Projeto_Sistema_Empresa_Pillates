from src.model.userModel.userConfig import Usuario
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.model.aulaModel.aulaConfig import Aula
from src.controllers.validations.statusSolicitacaoValidation import ValidarStatus
from src.schemas.solicitacao_schemas import SolicitacaoCreate, SolicitacaoUpdate, StatusSolcitacaoEnum, AcaoSolicitacaoAulaEnum, AcaoSolicitacaoPlanoEnum

from sqlalchemy.orm import relationship, Mapped, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete, func, update

from typing import Optional, Dict
from datetime import datetime
import logging


from src.database.connPostGreNeon import CreateSessionPostGre


class SolicitacoesModel():
    def __init__(self, session_db: Session):
        self.session_db = session_db

    def create_solicitacao(self, solicitacao_data:SolicitacaoCreate) ->Optional[Solicitacoes]:
        try:
            self.data_to_insert = solicitacao_data.model_dump(by_alias=False)
            self.new_solicitacao = Solicitacoes(**self.data_to_insert)
            
            self.session_db.add(self.new_solicitacao)
            self.session_db.commit()
            self.session_db.refresh(self.new_solicitacao) 
            return self.new_solicitacao
        
        except SQLAlchemyError as err:
            self.session_db.rollback()
            print(f'Erro ao criar nova solicitacao: {err}')
            return None
        except Exception as err:
            self.session_db.rollback()
            print(f'Erro ao processar a criação da solicitação: {err}')
            return None
        

    def delete_solicitacao(self, id_solicitacao:int):
        try:
            if id_solicitacao is None:
                print(f'Id invalido para excecução: {id_solicitacao}')
                return None
            self.stmt = delete(Solicitacoes).where(Solicitacoes.id_solicitacao == id_solicitacao)
            self.res_delete = self.session_db.execute(self.stmt)
            if self.res_delete.rowcount > 0:
                self.session_db.commit()
                print(f'Sucesso ao excluir solicitação')
                return True
            else:
                return False
            
        except SQLAlchemyError as err:
            self.session_db.rollback()
            print(f'Erro ao excluir solcitação do banco de dados: {err}')
            return None
        except Exception as err:
            self.session_db.rollback()
            print(f'Erro ao processar o pedido de delete da solicitação: {err}')
            return None

    def update_solicitacao(self, id_solcitacao:int, solicitacao_data:SolicitacaoUpdate)->Optional[Solicitacoes]:
        try:
            # res=str(self.status_update.value)
            # print(f'{type(res)}')           
            
            self.status_update = solicitacao_data.status_solicitacao
            self.dict_values_update = solicitacao_data.model_dump(exclude_none=True)
            # status_validos = {chave.value for chave in StatusSolcitacaoEnum}

            # if self.status_update.value not in status_validos:
            #     print(f'Erro ao aplicar tipo status da solicitação')
            #     return None
            
            self.dict_values_update["data_resposta"] = datetime.now()
    
            self.stmt_update = update(Solicitacoes).where(Solicitacoes.id_solicitacao == id_solcitacao).values(**self.dict_values_update).returning(Solicitacoes)
            self.updated_solcitacao = self.session_db.execute(self.stmt_update).scalar_one_or_none()
            if self.updated_solcitacao:
                self.session_db.commit()
                print(f'Sucesso ao alterar status da solicitação')
                return self.updated_solcitacao
            return None
        
        except SQLAlchemyError as err:
            self.session_db.rollback()
            print(f'Erro ao atualizar tabela: {err}')
            return None
        except Exception as err:
            print(f'Erro ao processar dados para atualização: {err}')
            self.session_db.rollback()
            return None

    def select_all_solicitacoes(self, id_estudio:int | None = None)->list[Solicitacoes]:
        try:
            if id_estudio is None:
                stmt = select(Solicitacoes).order_by(Solicitacoes.id_solicitacao)
            else:
                stmt = select(Solicitacoes).where(Solicitacoes.fk_id_estudio == id_estudio).order_by(Solicitacoes.id_solicitacao)
            results = self.session_db.execute(stmt).unique().scalars().all()
            return results
        except SQLAlchemyError as err:
            self.session_db.rollback()
            print(f'Erro ao atualizar tabela: {err}')
            return []
        except Exception as err:
            print(f'Erro ao atualizar tabela: {err}')
            self.session_db.rollback()
            return None

    def select_solicitacao_by_id(self, id_solicitacao: int) -> Optional[Solicitacoes]:
        try:
            stmt = select(Solicitacoes).where(Solicitacoes.id_solicitacao == id_solicitacao)
            result = self.session_db.execute(stmt).unique().scalar_one_or_none()
            
            return result
        except SQLAlchemyError as err:
            logging.error(f'Erro ao buscar solicitação {id_solicitacao}: {err}')
            return None
        except Exception as err:
            logging.error(f'Erro inesperado ao buscar solicitação {id_solicitacao}: {err}')
            return None


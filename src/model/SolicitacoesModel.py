from src.model.userModel.userConfig import Usuario
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes

from src.schemas.solicitacao_schemas import Solicitacao, SolicitacaoCreate, SolicitacaoUpdate

from sqlalchemy.orm import relationship, Mapped, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete, func, update

from typing import Optional, Dict




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
    def delete_solicitacao(self, id_solicitacao):
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
            self.session_db.rollback
            print(f'Erro ao excluir solcitação do banco de dados: {err}')
            return None
        except Exception as err:
            self.session_db.rollback()
            print(f'Erro ao processar o pedido de delete da solicitação: {err}')
            return None

    def update_solicitacao(self, id_solcitacao, solicitacao_data):
        pass

    def select_all_solicitacoes(self, id_estudio):
        pass
    def select_solcitacao(self, id):
        pass


# from src.schemas.solicitacao_schemas import TipoDeSolicitacaoEnum
# create_sesison = CreateSessionPostGre()
# session = create_sesison.get_session()

# try:
#     model_solcitacao = SolicitacoesModel(session_db=session)
#     # values = SolicitacaoCreate(
#     #     fk_id_user=1,
#     #     fk_id_estudio=1,
#     #     menssagem='testesssss',
#     #     tipo_de_solicitacao=TipoDeSolicitacaoEnum.AULA

#     # )
#     # nova_solicitacao = model_solcitacao.create_solicitacao(values)
#     res_delete = model_solcitacao.delete_solicitacao(1)
#     if res_delete:
#         print(res_delete)
#     else:
#         print(res_delete)
    

# except SQLAlchemyError as err:
#     print(f'Erro ao {err}')

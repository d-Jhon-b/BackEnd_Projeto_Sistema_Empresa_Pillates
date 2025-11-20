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


        
    # def select_solcitacao(self, id):
    #     pass




# from src.model.SolicitacoesModel import SolicitacoesModel # Importar o modelo
# from src.schemas.solicitacao_schemas import SolicitacaoCreate, TipoDeSolicitacaoEnum


# create_session =CreateSessionPostGre()
# session = create_session.get_session()


# solicitacoes_repo = SolicitacoesModel(session_db=session)
# FK_ESTUDANTE = 1
# FK_ESTUDIO = 1
# FK_AULA_EXISTENTE = 1
# FK_PLANO_PADRAO = 1
# FK_PLANO_PERSONALIZADO = 1
# DATA_SUGERIDA = datetime.now().replace(minute=0, second=0, microsecond=0)


# solicitacao_agendamento = SolicitacaoCreate(
#     fk_id_estudante=FK_ESTUDANTE,
#     fk_id_estudio=FK_ESTUDIO,
#     menssagem="Agendar aula experimental para teste.",
#     tipo_de_solicitacao=TipoDeSolicitacaoEnum.AULA,
#     acao_solicitacao_aula=AcaoSolicitacaoAulaEnum.AGENDAMENTO,
#     data_sugerida=DATA_SUGERIDA
# )
# try:
#     new_solicitacao = solicitacoes_repo.create_solicitacao(solicitacao_agendamento)
#     if new_solicitacao:
#         print(f"SUCESSO 1 (AGENDAMENTO): ID {new_solicitacao.id_solicitacao} | Tipo: {new_solicitacao.tipo_de_solicitacao} | Ação: {new_solicitacao.acao_solicitacao_aula}")
#     else:
#         print("FALHA 1 (AGENDAMENTO): Retornou None.")
# except Exception as e:
#     print(f"ERRO 1 (AGENDAMENTO): {e}")




# solicitacao_cancelamento = SolicitacaoCreate(
#     fk_id_estudante=FK_ESTUDANTE,
#     fk_id_estudio=FK_ESTUDIO,
#     menssagem="Não poderei comparecer à aula de amanhã.",
#     tipo_de_solicitacao=TipoDeSolicitacaoEnum.AULA,
#     acao_solicitacao_aula=AcaoSolicitacaoAulaEnum.CANCELAMENTO,
#     fk_id_aula_referencia=FK_AULA_EXISTENTE,
#     data_sugerida=DATA_SUGERIDA # Data sugerida ainda é necessária no Pydantic
# )
# try:
#     new_solicitacao = solicitacoes_repo.create_solicitacao(solicitacao_cancelamento)
#     if new_solicitacao:
#         print(f"SUCESSO 2 (CANCELAMENTO): ID {new_solicitacao.id_solicitacao} | Tipo: {new_solicitacao.tipo_de_solicitacao} | Ação: {new_solicitacao.acao_solicitacao_aula} | Aula Ref: {new_solicitacao.fk_id_aula_referencia}")
#     else:
#         print("FALHA 2 (CANCELAMENTO): Retornou None.")
# except Exception as e:
#     print(f"ERRO 2 (CANCELAMENTO): {e}")


# solicitacao_mudanca_padrao = SolicitacaoCreate(
#     fk_id_estudante=FK_ESTUDANTE,
#     fk_id_estudio=FK_ESTUDIO,
#     menssagem="Quero mudar para o plano trimestral.",
#     tipo_de_solicitacao=TipoDeSolicitacaoEnum.PLANO,
#     acao_solicitacao_plano=AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO,
#     fk_id_novo_plano=FK_PLANO_PADRAO,
#     data_sugerida=DATA_SUGERIDA # Data sugerida ainda é necessária no Pydantic
# )
# try:
#     new_solicitacao = solicitacoes_repo.create_solicitacao(solicitacao_mudanca_padrao)
#     if new_solicitacao:
#         print(f"SUCESSO 3 (MUDANÇA PADRÃO): ID {new_solicitacao.id_solicitacao} | Tipo: {new_solicitacao.tipo_de_solicitacao} | Ação: {new_solicitacao.acao_solicitacao_plano} | Novo Plano: {new_solicitacao.fk_id_novo_plano}")
#     else:
#         print("FALHA 3 (MUDANÇA PADRÃO): Retornou None.")
# except Exception as e:
#     print(f"ERRO 3 (MUDANÇA PADRÃO): {e}")


# solicitacao_renovacao_personalizado = SolicitacaoCreate(
#     fk_id_estudante=FK_ESTUDANTE,
#     fk_id_estudio=FK_ESTUDIO,
#     menssagem="Renovação do meu pacote personalizado.",
#     tipo_de_solicitacao=TipoDeSolicitacaoEnum.PLANO,
#     acao_solicitacao_plano=AcaoSolicitacaoPlanoEnum.RENOVACAO_PLANO,
#     fk_id_novo_plano_personalizado=FK_PLANO_PERSONALIZADO,
#     data_sugerida=DATA_SUGERIDA
# )
# try:
#     new_solicitacao = solicitacoes_repo.create_solicitacao(solicitacao_renovacao_personalizado)
#     if new_solicitacao:
#         print(f"SUCESSO 4 (RENOV. PERS.): ID {new_solicitacao.id_solicitacao} | Tipo: {new_solicitacao.tipo_de_solicitacao} | Ação: {new_solicitacao.acao_solicitacao_plano} | Novo Plano Pers.: {new_solicitacao.fk_id_novo_plano_personalizado}")
#     else:
#         print("FALHA 4 (RENOV. PERS.): Retornou None.")
# except Exception as e:
#     print(f"ERRO 4 (RENOV. PERS.): {e}")

# Usaremos o ID da primeira solicitação criada (AGENDAMENTO)

# new_solicitacao = 1

# if 'new_solicitacao' in locals() and new_solicitacao:
#     # solicitacao_id_para_update = new_solicitacao.id_solicitacao

# solicitacao_update_data = SolicitacaoUpdate(
#     status_solicitacao=StatusSolcitacaoEnum.Rec
# )
# solicitacao_id_para_update=13
# try:
#     updated_solicitacao = solicitacoes_repo.update_solicitacao(solicitacao_id_para_update, solicitacao_update_data)
#     if updated_solicitacao:
#         print(f"\nSUCESSO 5 (UPDATE): Solicitação ID {solicitacao_id_para_update} atualizada para STATUS: {updated_solicitacao.status_solicitacao} | Resposta em: {updated_solicitacao.data_resposta.strftime('%Y-%m-%d %H:%M')}")
#     else:
#         print(f"\nFALHA 5 (UPDATE): Não foi possível atualizar solicitação ID {solicitacao_id_para_update}.")
# except Exception as e:
#     print(f"\nERRO 5 (UPDATE): {e}")


# # Usaremos o ID da segunda solicitação criada (CANCELAMENTO)
# if 'solicitacao_cancelamento' in locals() and solicitacao_cancelamento:
#     solicitacao_id_para_delete = solicitacao_cancelamento.id_solicitacao
# solicitacao_id_para_delete =4   
# try:
#     delete_result = solicitacoes_repo.delete_solicitacao(solicitacao_id_para_delete)
#     if delete_result:
#         print(f"\nSUCESSO 6 (DELETE): Solicitação ID {solicitacao_id_para_delete} excluída.")
#     else:
#         print(f"\nFALHA 6 (DELETE): Solicitação ID {solicitacao_id_para_delete} não foi encontrada ou excluída.")
# except Exception as e:
#     print(f"\nERRO 6 (DELETE): {e}")

# session.close()
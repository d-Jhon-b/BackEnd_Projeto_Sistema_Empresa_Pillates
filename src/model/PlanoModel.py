from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante

from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.contratoConfig import Contrato


from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados

from src.schemas.plano_schemas import (ModalidadePlanoEnum, PlanoCreate, PlanoResponse, PlanoUpdate, TipoPlanoEnum)
from src.schemas.planos_personalizados_schemas import (PlanoPersonalizadoCreate, PlanoPersonalizadoResponse, PlanoPersonalizadoUpdate)
from datetime import date, datetime, timedelta
from typing import Dict, Union, Optional, List, Any
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import logging

#para teste
from src.database.connPostGreNeon import CreateSessionPostGre



class PlanosModel():
    def __init__(self, session_db:Session):
        self.session = session_db
        
    def insert_new_plano(self, data_to_insert: PlanoCreate) -> Planos:
        try:
            plano_data_dict = data_to_insert.model_dump(exclude_defaults=False)
            # plano_data_dict: Dict[str, Any] = data_to_insert.model_dump(exclude_defaults=False)
            new_plano = Planos(**plano_data_dict)

            self.session.add(new_plano)
            self.session.commit()
            self.session.refresh(new_plano)
            return new_plano
        

        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Falha de integridade ao criar Plano Padrão: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao criar Plano Padrão: {e}")

    def update_plano_data(self, plano_id: int, data_to_update: PlanoUpdate) -> Optional[Planos]:
        update_dict: Dict[str, Any] = data_to_update.model_dump(exclude_unset=True)

        if not update_dict:
            # Se não há dados para atualizar, retorne o objeto atual.
            return self.session.get(Planos, plano_id)
            
        try:
            update_stmt = (
                update(Planos)
                .where(Planos.id_plano == plano_id)
                .values(**update_dict)
            )
            
            # 2. Executa a atualização
            result = self.session.execute(update_stmt)
            
            # Se nenhuma linha foi afetada, o plano não existia
            if result.rowcount == 0:
                self.session.rollback()
                return None
                
            self.session.commit()
            
            # 3. Retorna o objeto atualizado (recarregado do DB)
            return self.session.get(Planos, plano_id)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao atualizar Plano Padrão: {e}")

    def select_plano_by_id(self, plano_id: int) -> Optional[Planos]:
        try:
            stmt = select(Planos).where(Planos.id_plano==plano_id)
            result_search = self.session.execute(stmt).unique().one_or_none()
            return result_search
        except SQLAlchemyError as err:
            logging.error(f'Erro ao procurar plano com id: {plano_id}\nErro:{err}')
            return None
        except Exception as err:
            logging.error(f'Erro ao procurar plano com id: {plano_id}\nErro:{err}')
            return None

    def select_all_planos(self) -> List[Planos]:
        try:
            stmt = select(Planos).order_by(Planos.id_plano)
            results_search = self.session.execute(stmt).scalars().all()
            return results_search
        
        except SQLAlchemyError as err:
            logging.error(f'{err}')
            return []

    def delete_plano_by_id(self, plano_id: int) -> bool:
        try:
            delete_stmt = delete(Planos).where(Planos.id_plano == plano_id)
            result = self.session.execute(delete_stmt)
            self.session.commit()
            if result.rowcount > 0:
                print(f'Sucesso ao aplicar exclusão do plano com id:{plano_id}')
                return True
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Não foi possível deletar o Plano Padrão. Existem contratos vinculados: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao deletar Plano Padrão: {e}")




from decimal import Decimal
create_session = CreateSessionPostGre()
session=create_session.get_session()


plano_padrao_data_test = {
    'tipo_plano': TipoPlanoEnum.MENSAL.value,
    'modalidade_plano': ModalidadePlanoEnum.DUAS_SEMANAS.value,
    'descricao_plano': 'Acesso de duas vezes por semana.',
    'valor_plano': Decimal('199.99'),
    'qtde_aulas_totais': 8
}

# try:
# # Instancia o Model (DAO)
#     planos_model = PlanosModel(session_db=session)

    # print(plano_padrao_data_test)


    # plano_create_schema = PlanoCreate(**plano_padrao_data_test)

    # print(plano_create_schema)
    # print("Tentando criar Plano Padrão...")
    # new_plano = planos_model.insert_new_plano(plano_create_schema)
    
    # print(f"Plano Padrão criado com sucesso! ID: {new_plano.id_plano} | Tipo: {new_plano.tipo_plano}")
    
#busca: 
    # results=planos_model.select_all_planos()
    # for a in results:
    #     print(a)
    # result = planos_model.select_plano_by_id(1)
    # print(result)

    #delete_plano_by id
# try:
# # Instancia o Model (DAO)
#     planos_model = PlanosModel(session_db=session)

#     delete_result = planos_model.delete_plano_by_id(5)
#     print(delete_result)

#     data_update = {
#         'tipo_plano': 'trimestral',
#         'valor_plano': 1
#     }
#     update_data_schema = PlanoUpdate(**data_update)

#     update_aplication = planos_model.update_plano_data(plano_id=1, data_to_update=update_data_schema)
#     print(f'{update_aplication}')
#     session.close()
# except SQLAlchemyError as err:
#     print(f'erro ao inserir plano no banco{err}')

# except Exception as err:
#     print(f'Erro ao aplicar inserção:{err}')


# data_adesao = datetime.now()
# tipo_plano = 'mensal' # Valor lido da tabela 'planos' via FK

# if tipo_plano == 'mensal':
#     data_validade = data_adesao + relativedelta(months=1)
# elif tipo_plano == 'trimestral':
#     data_validade = data_adesao + relativedelta(months=3)

# sa.Column('data_validade', sa.DateTime, nullable=False)
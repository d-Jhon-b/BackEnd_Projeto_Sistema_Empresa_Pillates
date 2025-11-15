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
            return self.session.get(Planos, plano_id)
            
        try:
            existing_plano = self.session.get(Planos, plano_id)
            if not existing_plano:
                return None
            
            for key, value in update_dict.items():
                setattr(existing_plano, key, value)
            
            self.session.commit()
            self.session.refresh(existing_plano)
            return existing_plano
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao atualizar Plano Padrão: {e}")

    def select_plano_by_id(self, plano_id: int) -> Optional[Planos]:
        try:
            return self.session.get(Planos, plano_id)
        except SQLAlchemyError:
            return None

    def select_all_planos(self) -> List[Planos]:
        try:
            stmt = select(Planos)
            return self.session.execute(stmt).scalars().all()
        except SQLAlchemyError:
            return []

    def delete_plano_by_id(self, plano_id: int) -> bool:
        try:
            delete_stmt = delete(Planos).where(Planos.id_plano == plano_id)
            result = self.session.execute(delete_stmt)
            self.session.commit()
            return result.rowcount > 0
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

try:
# Instancia o Model (DAO)
    planos_model = PlanosModel(session_db=session)

    print(plano_padrao_data_test)


    plano_create_schema = PlanoCreate(**plano_padrao_data_test)

    print(plano_create_schema)
    print("Tentando criar Plano Padrão...")
    new_plano = planos_model.insert_new_plano(plano_create_schema)
    
    print(f"Plano Padrão criado com sucesso! ID: {new_plano.id_plano} | Tipo: {new_plano.tipo_plano}")
    
    session.close()
except SQLAlchemyError as err:
    print(f'erro ao inserir plano no banco{err}')

except Exception as err:
    print(f'Erro ao aplicar inserção:{err}')


# data_adesao = datetime.now()
# tipo_plano = 'mensal' # Valor lido da tabela 'planos' via FK

# if tipo_plano == 'mensal':
#     data_validade = data_adesao + relativedelta(months=1)
# elif tipo_plano == 'trimestral':
#     data_validade = data_adesao + relativedelta(months=3)
# # ... etc.

# sa.Column('data_validade', sa.DateTime, nullable=False)
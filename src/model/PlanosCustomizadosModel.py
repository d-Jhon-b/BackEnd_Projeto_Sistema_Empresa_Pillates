from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.aluno import Estudante
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.contratoConfig import Contrato
from src.schemas.planos_personalizados_schemas import PlanoPersonalizadoCreate, PlanoPersonalizadoUpdate 

from src.database.connPostGreNeon import CreateSessionPostGre
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from decimal import Decimal
from datetime import datetime, timedelta



class PlanosPersonalizadosModel:
    """DAO para operações CRUD na tabela Planos Personalizados."""

    def __init__(self, session_db: Session):
        self.session = session_db

    def insert_new_plano(self, data_to_insert: PlanoPersonalizadoCreate) -> PlanosPersonalizados:
        """Insere um novo Plano Personalizado."""
        try:
            plano_data_dict: Dict[str, Any] = data_to_insert.model_dump(exclude_defaults=False)
            
            new_plano = PlanosPersonalizados(**plano_data_dict)
            self.session.add(new_plano)
            self.session.commit()
            self.session.refresh(new_plano)
            return new_plano
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Falha de integridade ao criar Plano Personalizado: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao criar Plano Personalizado: {e}")

    def update_plano_data(self, plano_id: int, data_to_update: PlanoPersonalizadoUpdate) -> Optional[PlanosPersonalizados]:
        """Atualiza um Plano Personalizado existente pelo ID."""

        update_dict: Dict[str, Any] = data_to_update.model_dump(exclude_unset=True)
        
        if not update_dict:
            return self.session.get(PlanosPersonalizados, plano_id)
            
        try:
            existing_plano = self.session.get(PlanosPersonalizados, plano_id)
            if not existing_plano:
                return None
            
            for key, value in update_dict.items():
                setattr(existing_plano, key, value)
            
            self.session.commit()
            self.session.refresh(existing_plano)
            return existing_plano
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao atualizar Plano Personalizado: {e}")

    def select_plano_by_id(self, plano_id: int) -> Optional[PlanosPersonalizados]:
        """Busca um Plano Personalizado pelo ID."""
        try:
            return self.session.get(PlanosPersonalizados, plano_id)
        except SQLAlchemyError:
            return None

    def select_all_planos(self) -> List[PlanosPersonalizados]:
        """Lista todos os Planos Personalizados."""
        try:
            stmt = select(PlanosPersonalizados)
            return self.session.execute(stmt).scalars().all()
        except SQLAlchemyError:
            return []

    def delete_plano_by_id(self, plano_id: int) -> bool:
        """Deleta um Plano Personalizado pelo ID."""
        try:
            delete_stmt = delete(PlanosPersonalizados).where(PlanosPersonalizados.id_plano_personalizado == plano_id)
            result = self.session.execute(delete_stmt)
            self.session.commit()
            return result.rowcount > 0
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Não foi possível deletar o Plano Personalizado. Existem contratos vinculados: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado no DB ao deletar Plano Personalizado: {e}")
        



# create_session = CreateSessionPostGre()
# session = create_session.get_session()

# def run_planos_personalizados_tests():    
#     plano_model = PlanosPersonalizadosModel(session_db=session)
#     new_plano_id = None
    
#     try:        
#         # Dados para criar um novo plano personalizado
#         ## # plano_create_data = {
#         ## #     'nome_plano': 'Plano VIP Mensal',
#         ## #     'tipo_plano_livre': 'Flex',
#         ## #     'modalidade_plano_livre': 'Qualquer dia',
#         ## #     'descricao_plano': 'Acesso livre a todas as aulas por 30 dias.',
#         ## #     'valor_plano': Decimal('550.00'),
#         ## #     'qtde_aulas_totais': 999,
#         ## #     'is_temporario': True,
#         ## #     'data_validade': datetime.now() + timedelta(days=30)
#         ## # }
#         ## 
#         ## # plano_create_schema = PlanoPersonalizadoCreate(**plano_create_data)
#         ## # new_plano = plano_model.insert_new_plano(plano_create_schema)
#         ## # new_plano_id = new_plano.id_plano_personalizado
        
        
#         # Busca o plano recém-criado
#         # found_plano = plano_model.select_plano_by_id(new_plano_id)
#         # if found_plano:
#         #     print(f" Plano encontrado: ID {found_plano.id_plano_personalizado} | Valor: {found_plano.valor_plano}")
#         # else:
#         #     print(f"Falha ao encontrar o plano com ID {new_plano_id}.")
#         #     return
        
#         # Dados para atualização parcial (PATCH)
#         ### plano_update_data = {
#         ###     'nome_plano': 'Plano VIP Trimestral',
#         ###     'valor_plano': Decimal('150.00') 
#         ### }
#         ##
#         ### update_schema = PlanoPersonalizadoUpdate(**plano_update_data)
#         ##
#         ### # Chamada ao Model para atualizar
#         ### updated_plano = plano_model.update_plano_data(plano_id=new_plano_id, data_to_update=update_schema)
#         ##
#         ### print(f"Plano atualizado com sucesso! Novo nome: {updated_plano.nome_plano} | Novo valor: {updated_plano.valor_plano}")

#         # Deleta o plano
#         delete_result = plano_model.delete_plano_by_id(new_plano_id)
        
#         if delete_result:
#             print(f"plano com ID {new_plano_id} deletado com sucesso!")
#         else:
#             print(f" Falha ao deletar o plano com ID {new_plano_id}.")

#         # Tenta buscar novamente para confirmar a deleção
#         confirm_deleted = plano_model.select_plano_by_id(new_plano_id)
#         if confirm_deleted is None:
#              print(" Confirmação: A busca retornou None após a deleção.")
#         else:
#              print("Falha na confirmação da deleção.")
             
#     except SQLAlchemyError as e:
#         print(f'Erro de Banco de Dados durante o teste: {e}')
#         session.rollback()
#     except Exception as e:
#         print(f'Erro geral durante o teste: {e}')
#     finally:
#         session.close()

# run_planos_personalizados_tests()
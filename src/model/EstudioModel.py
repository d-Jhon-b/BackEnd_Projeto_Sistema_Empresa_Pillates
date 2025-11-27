from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, insert, update, delete
from typing import Optional, List
from src.model.estudioModel.estudioConfig import Estudio # Seu modelo base
from src.schemas.estudio_schemas import EstudioCreateSchema, EstudioUpdateSchema

from src.database.connPostGreNeon import CreateSessionPostGre

class EstudioModel:
    def __init__(self, db_session: Session):
        self.session = db_session

    def create_estudio(self, estudio_data: EstudioCreateSchema) -> Estudio:
        try:
            data_to_insert = estudio_data.model_dump(by_alias=True)
            data_to_insert['endereco_estudio'] = data_to_insert.pop('endereco')
            data_to_insert['cep_estudio'] = data_to_insert.pop('cep')
            data_to_insert['mongo_registros_estudio'] = data_to_insert.pop('mongoRegistro')

            new_estudio = Estudio(**data_to_insert)
            self.session.add(new_estudio)
            self.session.commit()
            self.session.refresh(new_estudio)
            return new_estudio
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Erro ao criar Estúdio: {e}")
            raise e
        
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao criar Estúdio: {e}")
            raise e
        
        
    def select_estudio_by_id(self, estudio_id: int) -> Optional[Estudio]:
        """ Busca um estúdio pelo ID. """
        try:
            stmt = select(Estudio).where(Estudio.id_estudio == estudio_id)
            result = self.session.execute(stmt).scalar_one_or_none()
            return result
        except Exception as e:
            print(f"Erro ao buscar Estúdio (ID: {estudio_id}): {e}")
            return None
        
    def select_all_estudios(self) -> List[Estudio]:
        """ Retorna todos os estúdios. """
        try:
            stmt = select(Estudio).order_by(Estudio.id_estudio)
            results = self.session.execute(stmt).scalars().all()
            return results
        except Exception as e:
            print(f"Erro ao buscar todos os Estúdios: {e}")
            return []

    def update_estudio(self, estudio_id: int, update_data: EstudioUpdateSchema) -> Optional[Estudio]:
        try:
            data_to_update = update_data.model_dump(by_alias=True, exclude_none=True)
            
            if 'endereco' in data_to_update:
                data_to_update['endereco_estudio'] = data_to_update.pop('endereco')
            if 'cep' in data_to_update:
                data_to_update['cep_estudio'] = data_to_update.pop('cep')
            if 'mongoRegistro' in data_to_update:
                data_to_update['mongo_registros_estudio'] = data_to_update.pop('mongoRegistro')

            stmt = update(Estudio).where(Estudio.id_estudio == estudio_id).values(data_to_update).returning(Estudio)
            
            updated_estudio = self.session.execute(stmt).scalar_one_or_none()
            
            if updated_estudio:
                self.session.commit()
                return updated_estudio
            return None
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao atualizar Estúdio (ID: {estudio_id}): {e}")
            raise e

    def delete_estudio(self, estudio_id:int):
        if estudio_id is None:
            print('Estudio não definido para exclusão')
            return None 
        try:
            self.stmt = delete(Estudio).where(Estudio.id_estudio == estudio_id)
            self.res_delete = self.session.execute(self.stmt)
            if self.res_delete.rowcount>0:
                self.session.commit()
                print(f'Sucesso ao excluir o Estudio de ID: {estudio_id}')
                return True
            else:
                return False
            
        except SQLAlchemyError as err:
            print(f'Erro ao realizar operação {err}')
            self.session.rollback()
            return False
        



    def check_exists_by_id(self, estudio_id: int) -> bool:
        """ Verifica se um estúdio existe pelo seu ID (otimizado). """
        try:
            stmt = select(Estudio.id_estudio).where(Estudio.id_estudio == estudio_id)
            result = self.session.execute(stmt).scalar_one_or_none()
            return result is not None
        except Exception as e:
            print(f"Erro ao verificar Estúdio (ID: {estudio_id}): {e}")
            return False
        


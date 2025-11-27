from src.model.userModel.userConfig import Usuario
from src.model.userModel.typeUser.colaborador import Administracao, Recepcionista, Adm_plus

from datetime import date
from typing import Dict, Union, Optional, List
from sqlalchemy import select, func, delete, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

#para teste
from src.database.connPostGreNeon import CreateSessionPostGre



class ColaboradorModel:
    def __init__(self, db_session:Session):
        self.session = db_session

    def select_all_colaboradores(self, studio_id: int | None = None) -> list[Usuario]:
        try:
            stmt = (
                select(Usuario)
                .outerjoin(Administracao, Usuario.id_user == Administracao.fk_id_user)
                .outerjoin(Recepcionista, Usuario.id_user == Recepcionista.fk_id_user)
                .outerjoin(Adm_plus, Usuario.id_user == Adm_plus.fk_id_user)
                .where(or_(Administracao.fk_id_user.is_not(None), Recepcionista.fk_id_user.is_not(None),Adm_plus.fk_id_user.is_not(None))) 
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.administracao), 
                    joinedload(Usuario.recepcionista),
                    joinedload(Usuario.adm_plus)  
                )
            )
            
            if studio_id is not None:
                stmt = stmt.where(Usuario.fk_id_estudio == studio_id)

            resutls = self.session.execute(stmt)
            colaborador_list = resutls.scalars().unique().all()
            return colaborador_list
        
        except SQLAlchemyError as err:
            logging.error(f'Erro ao selecionar todos os colaboradores:\n{err}')
            return [] 

    def select_colaborador_by_id(self, user_id: int) -> Usuario | None:
        try:
            stmt = (
                select(Usuario)
                .where(Usuario.id_user == user_id)
                .outerjoin(Administracao, Usuario.id_user == Administracao.fk_id_user)
                .outerjoin(Recepcionista, Usuario.id_user == Recepcionista.fk_id_user)
                .outerjoin(Adm_plus, Usuario.id_user == Adm_plus.fk_id_user)
                .where(or_(Administracao.fk_id_user.is_not(None), Recepcionista.fk_id_user.is_not(None), Adm_plus.fk_id_user.is_not(None)))
                .options(
                    joinedload(Usuario.endereco),
                    joinedload(Usuario.contatos),
                    joinedload(Usuario.adm_plus),
                    joinedload(Usuario.administracao),
                    joinedload(Usuario.recepcionista),
                )
            )
            
            colaborador_value = self.session.execute(stmt).unique().scalar_one_or_none()
            return colaborador_value
            
        except SQLAlchemyError as err:
            logging.error(f'Erro ao buscar colaborador por ID:\n{err}')
            return None
        

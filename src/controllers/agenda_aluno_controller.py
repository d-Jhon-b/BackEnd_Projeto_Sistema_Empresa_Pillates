from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List,Optional
from datetime import datetime,date

from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository
from src.schemas.agenda_aluno_schemas import AgendaAlunoResponse
from src.controllers.utils.TargetUserFinder import TargetUserFinder 
import logging
from starlette.concurrency import run_in_threadpool # Para funções síncronas
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse,AgendaAlunoUpdate,StatusPresencaEnum
from src.repository.ContratoRepository import ContratoRepository
from src.controllers.validations.permissionValidation import UserValidation
from src.controllers.utils.TargetUserFinder import TargetUserFinder
from src.model.AgendaModel import AgendaAulaRepository 
from sqlalchemy.exc import SQLAlchemyError

class AgendaAlunoController:
    def __init__(self, db_session: Session, agenda_aluno_repo: AgendaAlunoRepository,agenda_aulas_repo: AgendaAulaRepository): 
        self.db_session = db_session
        self.agenda_repo = agenda_aluno_repo
        self.contrato_repo = ContratoRepository(db_session=db_session)

        self.agenda_aulas_repo = agenda_aulas_repo 


    # def __init__(self, agenda_repo: AgendaAlunoRepository, db_session: Session,contrato_repo: ContratoRepository):
        # self.contrato_repo = contrato_repo 

    async def get_agenda_by_estudante(
        self, 
        id_estudante: int, 
        data_inicio: datetime, 
        data_fim: datetime, 
        current_user: Dict[str, Any]
    ) -> List[AgendaAlunoResponse]:
        try:
            TargetUserFinder.check_and_get_target_user_id(
                session_db=self.db_session, 
                current_user=current_user, 
                estudante_id=id_estudante 
            )
            
            registros = await self.agenda_repo.find_registros_by_estudante_and_period(
                estudante_id=id_estudante,
                start_dt=data_inicio,
                end_dt=data_fim
            )
            
            return registros
            
        except HTTPException as err:
            raise err
        except Exception as err:
            logging.error(f'Erro ao buscar agenda do aluno {id_estudante}: {err}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao consultar a agenda do aluno.")
        

    async def update_status_presenca(
        self, 
        registro_id: str, 
        update_data: AgendaAlunoUpdate,
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        UserValidation._check_instrutor_permission(current_user=current_user)
        registro_original = await self.agenda_repo.select_registro_by_id(registro_id) 

        if not registro_original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de aula ID {registro_id} não encontrado."
            )

        estudante_id = registro_original.get("EstudanteID") 
        status_antigo = registro_original.get("StatusPresenca") 
        novo_status = update_data.status_presenca

        status_que_consomem = [StatusPresencaEnum.PRESENTE.value, StatusPresencaEnum.FALTA.value]
        
        deve_debitar = (
            novo_status in status_que_consomem and 
            status_antigo not in status_que_consomem
        )

        # if novo_status == "Presente" and status_antigo != "Presente":
        if deve_debitar:
            logging.info(f"Tentando debitar aula para Estudante ID: {estudante_id}")
            try:
                await run_in_threadpool(
                    self.contrato_repo.debitar_aula_do_plano, 
                    estudante_id
                )
                logging.info(f"Débito SQL realizado. Prosseguindo com a atualização no Mongo.")

            except ValueError as ve:
                logging.warning(f"ERRO DE NEGÓCIO (Débito): {ve}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{ve}. O registro de presença NÃO foi atualizado no Mongo."
                )
            
            except Exception as e:

                logging.error(f"Erro INESPERADO durante o débito no SQL: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno ao processar o débito da aula. O débito SQL falhou e foi revertido."
                )

        updated_registro = await self.agenda_repo.update_registro(
            registro_id, update_data
        )

        if not updated_registro:

            logging.critical("CRITICAL: Débito SQL realizado, mas falha ao atualizar Mongo!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ATENÇÃO: Débito da aula realizado, mas falha ao registrar presença no sistema. Contate o suporte!"
            )
            
        return updated_registro
    

    async def create_registro(self, data: AgendaAlunoCreate) -> Dict[str, Any]:
        """
        Cria um novo registro de aula na agenda do aluno (MongoDB).
        """
        try:
            registro_inserido = await self.agenda_repo.insert_registro(
                data.model_dump(by_alias=True, exclude_none=True)
            )
            
            if registro_inserido and "_id" in registro_inserido:
                registro_inserido["_id"] = str(registro_inserido["_id"]) # Converte ObjectId para string
                
            return registro_inserido
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao criar registro de aula.")

    async def get_student_agenda(
        self, 
        estudante_id: int, 
        current_user: dict, 
        agenda_aluno_repo: AgendaAlunoRepository, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[AgendaAlunoResponse]:

        # user_id = TargetUserFinder.check_and_get_target_user_id(session_db=self.db_session, estudante_id=estudante_id, current_user=current_user)
        # user_id = current_user.get("id_usuario")
        # user_lv_acesso = current_user.get("lv_acesso")
        

        # if (estudante_id != user_id) and (user_lv_acesso not in [NivelAcessoEnum.ADMIN.value, NivelAcessoEnum.SUPREMO.value]):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Você só pode acessar sua própria agenda, a menos que seja um administrador."
        #     )
        try:
            target_user_id = TargetUserFinder.check_and_get_target_user_id(
                session_db=self.db_session, 
                estudante_id=estudante_id, 
                current_user=current_user
            )
        except HTTPException as e:
            raise

        start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
        
        # 3. Busca no Repositório
        agenda_db = await agenda_aluno_repo.get_agenda_by_student_id(
            estudante_id=estudante_id, 
            start_date=start_dt, 
            end_date=end_dt
        )

        if not agenda_db:
            return [] # Retorna lista vazia se não houver registros
        
        # 4. Converte para Schema de Resposta
        return [AgendaAlunoResponse.model_validate(registro) for registro in agenda_db]
    


    async def delete_registro_agenda(
        self, 
        registro_id: str, 
        current_user: Dict[str, Any]
    ) -> bool:
        UserValidation._check_admin_permission(current_user) 
        success = await self.agenda_repo.delete_registro(registro_id=registro_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de aula ID {registro_id} não encontrado ou ID inválido."
            )
            
        return True

    async def delete_student_agenda_data(
        self,
        id_estudante: int,
        current_user: Dict[str, Any],
        #db_session:Session 
    ) -> Dict[str, Any]:
        UserValidation._check_admin_permission(current_user=current_user)
        
        sql_delete_success = False
        try:
            sql_delete_success = await run_in_threadpool(
                self.agenda_repo.delete_sql_registro_aula_estudante_by_id, 
                id_estudante, 
                self.db_session
            )
            
            if sql_delete_success is None:
                 raise SQLAlchemyError("Falha no método SQL do repositório.")
                 

        except SQLAlchemyError as e:
            logging.error(f"Erro SQL ao deletar agendamentos do estudante {id_estudante}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Erro ao deletar agendamentos do estudante no banco de dados SQL."
            )
        
        mongo_aluno_delete_count = 0
        try:
            mongo_aluno_delete_count = await self.agenda_repo.delete_mongo_registro_estudante_by_id(id_estudante)
        except Exception as e:
            logging.error(f"Erro Mongo (AgendaAluno) ao deletar registros do estudante {id_estudante}: {e}")
            
        mongo_aulas_modified_count = 0
        try:
            mongo_aulas_modified_count = await self.agenda_aulas_repo.remove_student_from_all_aulas(id_estudante)
        except Exception as e:
            logging.error(f"Erro Mongo CRÍTICO ao remover estudante {id_estudante} dos participantes (AgendaAulas): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A exclusão no SQL foi bem-sucedida, mas houve falha na limpeza da Agenda de Aulas do Estúdio (Mongo). Contate o suporte!"
            )

        logging.info(f"Exclusão total do estudante {id_estudante} concluída.")
        
        return {
            "message": f"Agendamentos do Estudante {id_estudante} excluídos com sucesso em todos os sistemas.",
            "sql_status": "Success",
            "sql_rows_affected": "Checado com sucesso", 
            "mongo_agenda_aluno_count": mongo_aluno_delete_count,
            "mongo_agenda_aulas_modified_count": mongo_aulas_modified_count
        }




    # async def create_registro(self, data: AgendaAlunoCreate) -> Dict[str, Any]:

    #     try:
    #         registro_inserido = await self.agenda_repo.insert_registro(
    #             data.model_dump(by_alias=True, exclude_none=True)
    #         )
            
    #         return registro_inserido
            
    #     except HTTPException as e:
    #         raise e
    #     except Exception as e:
    #         logging.error(f"Erro inesperado ao criar registro de aula: {e}")
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao criar registro de aula.")
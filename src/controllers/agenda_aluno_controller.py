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

from src.services.cloudinaryService import CloudinaryService 

class AgendaAlunoController:
    def __init__(self, db_session: Session, agenda_aluno_repo: AgendaAlunoRepository,agenda_aulas_repo: AgendaAulaRepository): 
        self.db_session = db_session
        self.agenda_repo = agenda_aluno_repo
        self.contrato_repo = ContratoRepository(db_session=db_session)
        self.agenda_aulas_repo = agenda_aulas_repo 
        self.cloudinary_service = CloudinaryService()


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
        
    async def _handle_anexos_upload(
        self, 
        registro_id: str, 
        estudante_id: int, 
        anexos: List[bytes]
    ) -> List[str]:
        if not anexos:
            return []
            
        uploaded_urls: List[str] = []
        
        for idx, file_bytes in enumerate(anexos):
            try:

                public_id = f"evolucao/{estudante_id}/{registro_id}_{idx}"
                folder = "anexos_evolucao"                
                secure_url = await self.cloudinary_service.upload_optimized_image(
                    file_contents=file_bytes, 
                    folder=folder, 
                    public_id=public_id
                )
                uploaded_urls.append(secure_url)
                
            except Exception as e:
                logging.error(f"Falha ao processar e subir o anexo {idx} para o Cloudinary: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Falha ao processar e enviar o anexo {idx} para a nuvem."
                )
                
        return uploaded_urls
    

    async def update_status_presenca(
        self, 
        registro_id: str, 
        update_data: AgendaAlunoUpdate,
        current_user: Dict[str, Any],
        anexos_files_bytes: Optional[List[bytes]] = None
    ) -> Dict[str, Any]:
        
        UserValidation._check_instrutor_permission(current_user=current_user)
        registro_original = await self.agenda_repo.select_registro_by_id(registro_id) 
        if not registro_original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de aula ID {registro_id} não encontrado."
            )

        estudante_id = registro_original.get("EstudanteID") 
        if anexos_files_bytes:
            
            new_anexos_urls = await self._handle_anexos_upload(
                registro_id=registro_id, 
                estudante_id=estudante_id, 
                anexos=anexos_files_bytes 
            )
            
            existing_anexos = registro_original.get("AnexosLinks", [])

            update_data.anexos_links = existing_anexos + new_anexos_urls


        status_antigo = registro_original.get("StatusPresenca") 
        novo_status = update_data.status_presenca

        status_que_consomem = [StatusPresencaEnum.PRESENTE.value, StatusPresencaEnum.FALTA.value]
        
        deve_debitar = (
            novo_status in status_que_consomem and 
            status_antigo not in status_que_consomem
        )

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
        
        agenda_db = await agenda_aluno_repo.get_agenda_by_student_id(
            estudante_id=estudante_id, 
            start_date=start_dt, 
            end_date=end_dt
        )

        if not agenda_db:
            return [] 
        
        return [AgendaAlunoResponse.model_validate(registro) for registro in agenda_db]
    

    async def get_students_agenda_by_ids(
        self, 
        student_ids: List[int], 
        class_date: date, 
        current_user: Dict[str, Any]
    ) -> List[AgendaAlunoResponse]:
        UserValidation._check_instrutor_permission(current_user=current_user)
        # if current_user.get("lv_acesso") not in ["instrutor", "colaborador", "supremo"]:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas instrutores e administradores podem ver a agenda de outros alunos.")

        start_dt = datetime.combine(class_date, datetime.min.time())
        end_dt = datetime.combine(class_date, datetime.max.time())
        
        try:
            registros = await self.agenda_repo.find_registros_by_multiple_students_and_period(
                estudante_ids=student_ids,
                start_dt=start_dt,
                end_dt=end_dt
            )
            
            return [AgendaAlunoResponse.model_validate(registro) for registro in registros]
            
        except Exception as err:
            logging.error(f'Erro ao buscar agendas dos alunos {student_ids} para a data {class_date}: {err}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao consultar as agendas dos alunos.")
        



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


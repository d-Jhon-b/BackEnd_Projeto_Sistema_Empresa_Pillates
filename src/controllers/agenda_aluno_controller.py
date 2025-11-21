from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository
from src.schemas.agenda_aluno_schemas import AgendaAlunoResponse
from src.controllers.utils.TargetUserFinder import TargetUserFinder 
import logging
from starlette.concurrency import run_in_threadpool # Para funções síncronas
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse,AgendaAlunoUpdate
from src.repository.ContratoRepository import ContratoRepository


class AgendaAlunoController:
    def __init__(self, db_session: Session, agenda_aluno_repo: AgendaAlunoRepository): # <-- DEVE TER ESTES ARGUMENTOS
        self.db_session = db_session
        self.agenda_repo = agenda_aluno_repo
        # self.agenda_aluno_repo = agenda_aluno_repo

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
                estudante_id=id_estudante # Checa se o usuário logado tem acesso a este ID
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
        update_data: AgendaAlunoUpdate
    ) -> Dict[str, Any]:

        registro_original = await self.agenda_repo.select_registro_by_id(registro_id) 

        if not registro_original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de aula ID {registro_id} não encontrado."
            )

        estudante_id = registro_original.get("EstudanteID") 
        status_antigo = registro_original.get("StatusPresenca") 
        novo_status = update_data.status_presenca
        
        if novo_status == "Presente" and status_antigo != "Presente":
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

        # 3. Atualiza o Status no MongoDB (Executa APENAS se o débito foi OK ou se NÃO houve débito)
        updated_registro = await self.agenda_repo.update_registro(
            registro_id, update_data
        )

        if not updated_registro:
            # Isto é um erro grave, pois o SQL já debitou, mas o Mongo falhou.
            # Em sistemas de produção, isto exigiria um mecanismo de compensação (ex: estorno manual ou fila de mensagens).
            # Para este projeto, apenas levantamos o 500.
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
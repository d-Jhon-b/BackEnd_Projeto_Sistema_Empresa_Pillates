from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from datetime import datetime,date,timedelta

from starlette.concurrency import run_in_threadpool 
from dateutil.relativedelta import relativedelta 

from src.model.SolicitacoesModel import SolicitacoesModel

from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.model.planosModel.planoConfig import Planos
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.model.ContratoModel import ContratoModel

# from src.model.SolicitacoesModel import SolicitacoesModel
from src.model.AulaModel import AulaModel 
from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.model.PlanoModel import PlanosModel 
from src.model.AgendaModel import AgendaAulaRepository


from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import (UserResponse, 
LoginRequestSchema, 
NivelAcessoEnum, 
AlunoCreatePayload, 
InstrutorCreatePayload, 
ColaboradorCreatePayload,
)
from src.schemas.adesao_plano_schemas import SubscribePlanoPayload, SubscribePlano,AdesaoPlanoBase,AdesaoPlanoUpdate
from src.controllers.validations.permissionValidation import UserValidation
from src.schemas.solicitacao_schemas import SolicitacaoCreate, SolicitacaoUpdate, SolicitacaoResponseSchema, SolicitacaoCreatePayload, SolicitacoesBase,StatusSolcitacaoEnum,AcaoSolicitacaoAulaEnum,AcaoSolicitacaoPlanoEnum,TipoDeSolicitacaoEnum
from src.schemas.aulas_schemas import MatriculaCreate
from src.controllers.validations.statusSolicitacaoValidation import ValidarStatus
from src.services.AdesaoContratoService import AdesaoContratoService
from src.controllers.utils.TargetUserFinder import TargetUserFinder
import logging

class SolicitacaoController():
    def create_new_request(self, session_db:Session, data_request:SolicitacaoCreatePayload, current_user: Dict[str, Any]):
        UserValidation._check_all_permission(current_user)
        try:

            user_id = current_user.get("id_user")
            estudante_id=TargetUserFinder.check_id_estudante_by_id_user(session_db=session_db, user_id=user_id)

            fk_id_estudio = current_user.get("fk_id_estudio")

            if user_id is None or fk_id_estudio is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Dados do usuário inválidos."
                )
            

            solicitacao_data = SolicitacaoCreate(
                fk_id_estudante=estudante_id,
                fk_id_estudio=fk_id_estudio,
                menssagem=data_request.menssagem,
                tipo_de_solicitacao=data_request.tipo_de_solicitacao,
                
                acao_solicitacao_plano=data_request.acao_solicitacao_plano,
                acao_solicitacao_aula=data_request.acao_solicitacao_aula,
                
                fk_id_aula_referencia=data_request.fk_id_aula_referencia,
                data_sugerida=data_request.data_sugerida,
                
                fk_id_novo_plano=data_request.fk_id_novo_plano,
                fk_id_novo_plano_personalizado=data_request.fk_id_novo_plano_personalizado
            )

            solicitacao_model = SolicitacoesModel(session_db=session_db)
            new_request = solicitacao_model.create_solicitacao(solicitacao_data) # Usa o objeto SolicitacaoCreate completo

            return SolicitacaoResponseSchema.model_validate(new_request)

        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao criar solicitação: {err}"
            )
        
    def select_all_solicitacoes(self,session_db:Session,current_user:dict, id_estudio:int | None):
        UserValidation._check_admin_permission(current_user=current_user)
        fk_id_estudio = current_user.get('fk_id_estudio')
        try:
            solicitacoes_model=SolicitacoesModel(session_db=session_db)
            lv_acesso = current_user.get('lv_acesso')

            if id_estudio is None:
                if lv_acesso == NivelAcessoEnum.SUPREMO.value:
                    solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes() 
                else:
                    solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes(fk_id_estudio)
            else:
                solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes(id_estudio)
            return [SolicitacaoResponseSchema.model_validate(solicitacoes) for solicitacoes in solicitacoes_from_db]
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao processar solicitação de busca das solicitações: {err}"
            )

    async def handle_request_resolution(
        self, 
        id_solicitacao: int, 
        session_db: Session, 
        current_user: Dict[str, Any], 
        status_solicitacao: StatusSolcitacaoEnum, 
        agenda_repo: AgendaAulaRepository


    ) -> SolicitacaoResponseSchema:
        UserValidation._check_admin_permission(current_user)

        solicitacao_model = SolicitacoesModel(session_db=session_db)
        
        solicitacao_db: Optional[Solicitacoes] = await run_in_threadpool(
            solicitacao_model.select_solicitacao_by_id,
            id_solicitacao
        )
        if not solicitacao_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Solicitação ID {id_solicitacao} não encontrada.")
        
        if solicitacao_db.status_solicitacao in [StatusSolcitacaoEnum.ATENDIDA.value, StatusSolcitacaoEnum.RECUSADA.value]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solicitação já foi processada.")

        
        aula_model = AulaModel(db_session=session_db) 
        adesao_plano_model = AdesaoPlanoModel(session_db=session_db)
        contrato_model = ContratoModel(session_db=session_db) 
        
        try:
            if status_solicitacao == StatusSolcitacaoEnum.ATENDIDA:
                
                if solicitacao_db.tipo_de_solicitacao == "aula":
                    await self._process_aula_resolution( 
                        session_db, 
                        solicitacao_db, 
                        aula_model,
                        agenda_repo
                    )
                
                elif solicitacao_db.tipo_de_solicitacao == "plano":
                    await run_in_threadpool( 
                        self._process_plano_resolution,
                        session_db,
                        solicitacao_db,
                        adesao_plano_model,
                        contrato_model,
                        current_user 
                    )
                else:
                    if solicitacao_db.tipo_de_solicitacao not in ["pagamento", "outros"]:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de solicitação desconhecido ou sem ação de DB implementada: {solicitacao_db.tipo_de_solicitacao}")


            update_data = SolicitacaoUpdate(
                status_solicitacao=status_solicitacao, 
            )
        
        except HTTPException as err:
            logging.error(f'erro ao processar solcitação: {err}')
            session_db.rollback() 
            raise
        except Exception as e:
            session_db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro durante o processamento da solicitação {solicitacao_db.id_solicitacao}: {e}")

        updated_solicitacao = await run_in_threadpool(
            solicitacao_model.update_solicitacao,
            id_solicitacao,
            update_data
        )
        if not updated_solicitacao:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao atualizar o status da solicitação.")
              
        return SolicitacaoResponseSchema.model_validate(updated_solicitacao)

    async def _process_aula_resolution(
        self, 
        session_db: Session,
        solicitacao_db: Solicitacoes,
        aula_model: AulaModel,
        agenda_repo: AgendaAulaRepository 
    ):
        acao = solicitacao_db.acao_solicitacao_aula
        estudante_id = solicitacao_db.fk_id_estudante
        fk_id_aula_ref = solicitacao_db.fk_id_aula_referencia

        if acao == AcaoSolicitacaoAulaEnum.REAGENDAMENTO:
            
            if not fk_id_aula_ref:
                 raise ValueError("ID da aula de referência é obrigatório para reagendamento.")
            


            logging.info(f"Iniciando busca da data da aula antiga no Mongo (AulaID: {fk_id_aula_ref}, StudentID: {estudante_id})")
            data_aula_antiga = await agenda_repo.find_next_enrolled_aula_date(
                aula_id=fk_id_aula_ref,
                student_id=estudante_id 
            )

            if data_aula_antiga is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Aula de referência (ID: {solicitacao_db.fk_id_aula_referencia}) não encontrada no agendamento do aluno."
                )
            
            logging.info(f"Data antiga encontrada: {data_aula_antiga}. Nova data: {data_aula_antiga + timedelta(days=7)}")



            data_proxima_semana = data_aula_antiga + timedelta(days=7)
                    
            logging.info(f"Data antiga encontrada: {data_aula_antiga}. Nova data calculada: {data_proxima_semana}")
            

            aula_antiga_mongo = await agenda_repo.find_aula_by_id_and_date(
                aula_id=fk_id_aula_ref,
                date_time=data_aula_antiga 
            )
            
            titulo_aula_recorrente = aula_antiga_mongo.get("tituloAulaCompleto") if aula_antiga_mongo else None
            
            if not titulo_aula_recorrente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Não foi possível reagendar: Título da aula original não encontrado para buscar a próxima ocorrência."
                ) 

            logging.info(f"Buscando próxima ocorrência por TÍTULO ('{titulo_aula_recorrente}') na data {data_proxima_semana}")
            
            proxima_aula_mongo = await agenda_repo.find_aula_by_titulo_and_date(
                titulo_aula=titulo_aula_recorrente,
                date_time=data_proxima_semana 
            )

            if proxima_aula_mongo is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível reagendar: A ocorrência desta aula na próxima semana não foi encontrada no calendário."
                )
                
            fk_id_nova_aula = proxima_aula_mongo["AulaID"] 
            logging.info(f"Ocorrência da próxima semana encontrada com o NOVO ID: {fk_id_nova_aula}")

            removed_success = await agenda_repo.remove_participant_by_date(
                aula_id=fk_id_aula_ref,
                participant_id=estudante_id,
                aula_date=data_aula_antiga
            )
            logging.info(f"Resultado da remoção: {removed_success}")
            if not removed_success:
                 logging.warning(f"Estudante {estudante_id} não estava na lista de participantes da aula {fk_id_aula_ref} na data {data_aula_antiga}, mas o reagendamento continuará.")

            
            logging.info(f"Tentando adicionar estudante à nova aula em {data_proxima_semana}")
            updated_aula_success = await agenda_repo.add_participant_by_date(
                aula_id=fk_id_nova_aula,
                participant_id=estudante_id,
                aula_date=data_proxima_semana
            )
            
            if not updated_aula_success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Falha ao adicionar estudante à próxima aula agendada no Mongo."
                )
                
            logging.info(f"Estudante {estudante_id} reagendado (removido da data {data_aula_antiga} e adicionado em {data_proxima_semana}).")

        elif acao == AcaoSolicitacaoAulaEnum.CANCELAMENTO:
            
            if not fk_id_aula_ref:
                 raise ValueError("ID da aula de referência é obrigatório para cancelamento.")
            
            if not data_aula_antiga: 
                logging.info(f"data_sugerida não fornecida para cancelamento. Buscando próxima aula para {fk_id_aula_ref}.")
                data_aula_cancelar = await agenda_repo.find_next_enrolled_aula_date(
                    aula_id=fk_id_aula_ref,
                    student_id=estudante_id 
                )
            else:
                data_aula_cancelar = data_aula_antiga
            
            if not data_aula_cancelar:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possível identificar a aula a ser cancelada (data_sugerida ausente e próxima aula não encontrada).")

            aula_cancelar_mongo = await agenda_repo.find_aula_by_id_and_date(
                aula_id=fk_id_aula_ref,
                date_time=data_aula_cancelar
            )
            
            if not aula_cancelar_mongo:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ocorrência da Aula ID {fk_id_aula_ref} na data {data_aula_cancelar.date()} não encontrada no Mongo.")

            removed_success = await agenda_repo.remove_participant_by_date(
                aula_id=fk_id_aula_ref,
                participant_id=estudante_id,
                aula_date=aula_cancelar_mongo.get("dataAgendaAula") 
            )
            
            if not removed_success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno não estava matriculado nesta aula ou falha na remoção do Mongo.")      
            
            logging.info(f"Estudante {estudante_id} cancelou sua participação na Aula ID {fk_id_aula_ref} em {data_aula_cancelar.date()}.")
            
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ação de aula '{acao.value}' inválida ou não implementada para a resolução de solicitação.")
    
    def _process_plano_resolution(
        self, 
        session_db: Session, 
        solicitacao_db: Solicitacoes, 
        adesao_plano_model: AdesaoPlanoModel, 
        contrato_model: ContratoModel,
        current_user: Dict[str, Any]
    ): 
        
        adesao_contrato_service = AdesaoContratoService(db_session=session_db)

        estudante_id = solicitacao_db.fk_id_estudante
        acao = solicitacao_db.acao_solicitacao_plano

        if not acao:
            raise ValueError("Ação de plano ausente na solicitação.")

        contrato_ativo = contrato_model.select_active_contract_by_estudante(estudante_id)
        
        if acao == AcaoSolicitacaoPlanoEnum.CANCELAMENTO_PLANO:
            if not contrato_ativo:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum contrato ativo para ser cancelado.")

            contrato_model.update_contract_status(contrato_ativo.id_contrato, "cancelado")

        elif acao in [AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO, AcaoSolicitacaoPlanoEnum.RENOVACAO_PLANO]:
            
            fk_id_novo_plano = solicitacao_db.fk_id_novo_plano
            fk_id_plano_personalizado = solicitacao_db.fk_id_novo_plano_personalizado
            
            if not (fk_id_novo_plano or fk_id_plano_personalizado):
                raise ValueError("Novo plano ID (Padrão ou Personalizado) é obrigatório para Mudança/Renovação.")

            if acao == AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO and contrato_ativo:
                 contrato_model.update_contract_status(contrato_ativo.id_contrato, "cancelado")

            payload_adesao = {
                "fk_id_estudante": estudante_id,
                "fk_id_plano_Geral": { 
                    "fk_id_plano": fk_id_novo_plano,
                    "fk_id_plano_personalizado": fk_id_plano_personalizado
                }
            }
            
            try:
                adesao_data = SubscribePlanoPayload.model_validate(payload_adesao)
            except Exception as e:
                raise ValueError(f"Erro ao validar dados do plano para o service: {e}")

            adesao_contrato_service.create_adesao_and_contract(
                data=adesao_data, 
                estudante_id=estudante_id, 
                current_user=current_user
            )

        else:
            raise ValueError(f"Ação de plano '{acao.value}' inválida.")
        

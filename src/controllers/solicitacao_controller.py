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

            # solicitacao_model = SolicitacoesModel(session_db=session_db)
            # request_data_dict = data_request.model_dump(exclude_none=True)
            
            # request_data_dict['fk_id_estudante'] = user_id 
            # request_data_dict['fk_id_estudio'] = fk_id_estudio
            # solicitacao_data_full = SolicitacaoCreate(**request_data_dict)
            # new_request = solicitacao_model.create_solicitacao(solicitacao_data_full) # Usa o objeto SolicitacaoCreate completo

            # return SolicitacaoResponseSchema.model_validate(new_request)

        
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
            # if id_estudio is None:
            #     solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes(fk_id_estudio)
            if id_estudio is None:
                if lv_acesso == NivelAcessoEnum.SUPREMO.value:
                    solicitacoes_from_db = solicitacoes_model.select_all_solicitacoes() #Vai buscar todas as solicitações de todos os estudios
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
                    await run_in_threadpool( # Chamada para o método atualizado de plano
                        self._process_plano_resolution,
                        session_db,
                        solicitacao_db,
                        adesao_plano_model,
                        contrato_model,
                        current_user # PASSANDO O current_user
                    )
                else:
                    if solicitacao_db.tipo_de_solicitacao not in ["pagamento", "outros"]:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de solicitação desconhecido ou sem ação de DB implementada: {solicitacao_db.tipo_de_solicitacao}")


            # 4. Dados para Atualizar (ATENDIDA ou RECUSADA)
            update_data = SolicitacaoUpdate(
                status_solicitacao=status_solicitacao, # Usa o status fornecido
            )
        
        except HTTPException:
            session_db.rollback() 
            raise
        except Exception as e:
            session_db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro durante o processamento da solicitação {solicitacao_db.id_solicitacao}: {e}")

        # 5. Persiste a atualização do status e retorna
        updated_solicitacao = await run_in_threadpool(
            solicitacao_model.update_solicitacao,
            id_solicitacao,
            update_data
        )
        if not updated_solicitacao:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao atualizar o status da solicitação.")
              
        return SolicitacaoResponseSchema.model_validate(updated_solicitacao)


    # ... (_process_aula_resolution mantido) ...
    
    def _process_plano_resolution(
        self, 
        session_db: Session, 
        solicitacao_db: Solicitacoes, 
        adesao_plano_model: AdesaoPlanoModel, # Mantido, mas não usado diretamente para criar adesão
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

            # Cancela o contrato existente
            contrato_model.update_contract_status(contrato_ativo.id_contrato, "cancelado")

        elif acao in [AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO, AcaoSolicitacaoPlanoEnum.RENOVACAO_PLANO]:
            
            fk_id_novo_plano = solicitacao_db.fk_id_novo_plano
            fk_id_plano_personalizado = solicitacao_db.fk_id_novo_plano_personalizado
            
            if not (fk_id_novo_plano or fk_id_plano_personalizado):
                raise ValueError("Novo plano ID (Padrão ou Personalizado) é obrigatório para Mudança/Renovação.")

            if acao == AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO and contrato_ativo:
                 # Cancela o contrato antigo antes de criar o novo
                 contrato_model.update_contract_status(contrato_ativo.id_contrato, "cancelado")

            # 1. Monta o Payload para o Service (simulando o que viria do endpoint de Adesão)
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

            # 2. Chama o Service para realizar a transação completa (Adesão, Contrato, Pagamentos)
            adesao_contrato_service.create_adesao_and_contract(
                data=adesao_data, 
                estudante_id=estudante_id, 
                current_user=current_user
            )

        else:
            raise ValueError(f"Ação de plano '{acao.value}' inválida.")
        

    # async def handle_request_resolution(
    #     self, 
    #     id_solicitacao: int, 
    #     session_db: Session, 
    #     current_user: Dict[str, Any], 
    #     status_solicitacao: StatusSolcitacaoEnum, 
    #     agenda_repo: AgendaAulaRepository
    # ) -> SolicitacaoResponseSchema:
    #     UserValidation._check_admin_permission(current_user)

    #     solicitacao_model = SolicitacoesModel(session_db=session_db)
        
    #     solicitacao_db: Optional[Solicitacoes] = await run_in_threadpool(
    #         solicitacao_model.select_solicitacao_by_id,
    #         id_solicitacao
    #     )
    #     if not solicitacao_db:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Solicitação ID {id_solicitacao} não encontrada.")
        
    #     if solicitacao_db.status_solicitacao in [StatusSolcitacaoEnum.ATENDIDA.value, StatusSolcitacaoEnum.RECUSADA.value]:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solicitação já foi processada.")

        
    #     aula_model = AulaModel(db_session=session_db) 
    #     adesao_plano_model = AdesaoPlanoModel(session_db=session_db)
    #     contrato_model = ContratoModel(db_session=session_db) # Instância do ContratoModel
        
    #     try:
    #         if status_solicitacao == StatusSolcitacaoEnum.ATENDIDA:
                
    #             if solicitacao_db.tipo_de_solicitacao == "aula":
    #                 await self._process_aula_resolution( # Chamada para o método atualizado
    #                     session_db, 
    #                     solicitacao_db, 
    #                     aula_model,
    #                     agenda_repo
    #                 )
                
    #             elif solicitacao_db.tipo_de_solicitacao == "plano":
    #                 await run_in_threadpool( # Chamada para o método atualizado de plano
    #                     self._process_plano_resolution,
    #                     session_db,
    #                     solicitacao_db,
    #                     adesao_plano_model,
    #                     contrato_model
    #                 )
    #             else:
    #                 # Tipo 'pagamento' ou 'outros' não exigem ação de DB complexa,
    #                 # apenas marcam como ATENDIDA.
    #                 if solicitacao_db.tipo_de_solicitacao not in ["pagamento", "outros"]:
    #                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de solicitação desconhecido ou sem ação de DB implementada: {solicitacao_db.tipo_de_solicitacao}")


    #         # 4. Dados para Atualizar (ATENDIDA ou RECUSADA)
    #         update_data = SolicitacaoUpdate(
    #             status_solicitacao=status_solicitacao, # Usa o status fornecido
    #         )
        
    #     except HTTPException:
    #         session_db.rollback() # Garante o rollback em caso de erro no processamento
    #         raise
    #     except Exception as e:
    #         session_db.rollback()
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro durante o processamento da solicitação {solicitacao_db.id_solicitacao}: {e}")

    #     # 5. Persiste a atualização do status e retorna
    #     updated_solicitacao = await run_in_threadpool(
    #         solicitacao_model.update_solicitacao,
    #         id_solicitacao,
    #         update_data
    #     )
    #     if not updated_solicitacao:
    #          raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao atualizar o status da solicitação.")
             
    #     return SolicitacaoResponseSchema.model_validate(updated_solicitacao)


    # # --- MÉTODOS DE SUPORTE (Chamando as Models/Repos Diretamente) ---

    # # RENOMEADO E ATUALIZADO
    # async def _process_aula_resolution(
    #     self, 
    #     session_db: Session, 
    #     solicitacao_db:Solicitacoes, 
    #     aula_model: AulaModel, 
    #     agenda_repo: AgendaAulaRepository
    # ):
    #     estudante_id = solicitacao_db.fk_id_estudante
    #     acao = solicitacao_db.acao_solicitacao_aula
        
    #     if not acao:
    #          raise ValueError("Ação de aula ausente na solicitação.")

    #     if acao == AcaoSolicitacaoAulaEnum.AGENDAMENTO:
    #         fk_id_aula = solicitacao_db.fk_id_aula_referencia
    #         if not fk_id_aula:
    #             raise ValueError("ID da aula de referência é obrigatório para AGENDAMENTO.")
            
    #         matricula_dict = MatriculaCreate(fk_id_estudante=estudante_id).model_dump(exclude_none=True)
            
    #         await run_in_threadpool(aula_model.enroll_student, fk_id_aula, matricula_dict)
    #         await agenda_repo.add_participant(aula_id=fk_id_aula, participant_id=estudante_id)
            
    #     elif acao in [AcaoSolicitacaoAulaEnum.CANCELAMENTO, AcaoSolicitacaoAulaEnum.REAGENDAMENTO]:
    #         fk_id_aula_antiga = solicitacao_db.fk_id_aula_referencia
            
    #         if not fk_id_aula_antiga:
    #             raise ValueError(f"ID da aula de referência é obrigatório para {acao.value}.")
            
    #         # 1. Validação de tempo (3 horas antes)
    #         aula_antiga_db = await run_in_threadpool(aula_model.select_aula_by_id, fk_id_aula_antiga)
    #         if not aula_antiga_db:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Aula ID {fk_id_aula_antiga} de referência não encontrada.")
            
    #         data_aula = aula_antiga_db.data_aula
    #         if data_aula - datetime.now() < timedelta(hours=3):
    #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
    #                                 detail=f"Ação de {acao.value} deve ser solicitada com pelo menos 3 horas de antecedência. Data da aula: {data_aula.strftime('%d/%m %H:%M')}")
            
    #         await run_in_threadpool(aula_model.unenroll_student, fk_id_aula_antiga, estudante_id)
    #         await agenda_repo.remove_participant(aula_id=fk_id_aula_antiga, participant_id=estudante_id)
            
    #         if acao == AcaoSolicitacaoAulaEnum.REAGENDAMENTO:
    #             pass 

    #     else:
    #         raise ValueError(f"Ação de aula '{acao.value}' inválida.")


    # def _process_plano_resolution(
    #     self, 
    #     session_db: Session, 
    #     solicitacao_db: Solicitacoes, 
    #     adesao_plano_model: AdesaoPlanoModel,
    #     contrato_model: ContratoModel
    # ): 
    #     plano_model = PlanosModel(session_db=session_db)
    #     estudante_id = solicitacao_db.fk_id_estudante
    #     acao = solicitacao_db.acao_solicitacao_plano

    #     if not acao:
    #          raise ValueError("Ação de plano ausente na solicitação.")

    #     contrato_ativo = contrato_model.select_active_contract_by_estudante(estudante_id)
        
    #     if acao == AcaoSolicitacaoPlanoEnum.CANCELAMENTO_PLANO:
    #         if not contrato_ativo:
    #              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum contrato ativo para ser cancelado.")

    #         contrato_model.update_contract_status(contrato_ativo.id_contrato, "cancelado")

    #     elif acao in [AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO, AcaoSolicitacaoPlanoEnum.RENOVACAO_PLANO]:
            
    #         fk_id_novo_plano = solicitacao_db.fk_id_novo_plano
    #         fk_id_plano_personalizado = solicitacao_db.fk_id_novo_plano_personalizado
            
    #         if not (fk_id_novo_plano or fk_id_plano_personalizado):
    #             raise ValueError("Novo plano ID (Padrão ou Personalizado) é obrigatório para Mudança/Renovação.")

    #         if acao == AcaoSolicitacaoPlanoEnum.MUDANCA_PLANO and contrato_ativo:
    #              contrato_model.update_contract_status(contrato_ativo.id_contrato, "cancelado")

    #         plano_obj = None
    #         if fk_id_novo_plano:
    #             plano_obj = plano_model.select_plano_by_id(fk_id_novo_plano)
    #             if not plano_obj:
    #                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Padrão ID {fk_id_novo_plano} não encontrado.")
    #             tipo_plano = plano_obj.tipo_plano.value
    #         elif fk_id_plano_personalizado:
    #             # Assumindo que você tem um método para buscar Plano Personalizado
    #             plano_obj = plano_model.select_plano_personalizado_by_id(fk_id_plano_personalizado)
    #             if not plano_obj:
    #                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Personalizado ID {fk_id_plano_personalizado} não encontrado.")
    #             tipo_plano = plano_obj.tipo_plano_livre # Usa o campo string livre ou define 'mensal' como padrão
    #         else:
    #              raise ValueError("Plano inválido para Mudança/Renovação.")
                 
            
    #         data_adesao = datetime.now()
    #         # 3. Lógica de cálculo de validade (semestral, trimestral, etc.)
    #         # Nota: Essa lógica deve ser mais completa, mas mantendo a simplicidade para o exemplo:
    #         if tipo_plano == 'mensal' or 'mensal' in tipo_plano.lower():
    #             data_validade_calc = data_adesao + relativedelta(months=1)
    #         elif 'trimestral' in tipo_plano.lower():
    #             data_validade_calc = data_adesao + relativedelta(months=3)
    #         elif 'semestral' in tipo_plano.lower():
    #             data_validade_calc = data_adesao + relativedelta(months=6)
    #         elif 'anual' in tipo_plano.lower():
    #             data_validade_calc = data_adesao + relativedelta(years=1)
    #         else:
    #             data_validade_calc = data_adesao + relativedelta(months=1) # Padrão
                

    #         # 4. Criação da Adesão
    #         dados_adesao = {
    #             "fk_id_estudante": estudante_id,
    #             "fk_id_plano": fk_id_novo_plano,
    #             "fk_id_plano_personalizado": fk_id_plano_personalizado,
    #             "data_validade": data_validade_calc
    #         }
    #         new_adesao = adesao_plano_model.subscribe_plan(dados_adesao)
    #         if not new_adesao:
    #              raise Exception("Falha na persistência da nova adesão no banco de dados.")

    #         # 5. Criação do Contrato (Isso deve ser feito após a Adesão, geralmente em cascata ou no mesmo fluxo)
    #         # Para o Contrato, você precisaria do valor do plano e qtde de aulas.
    #         valor_final = plano_obj.valor_plano
    #         qtde_aulas = plano_obj.qtde_aulas_totais
            
    #         contrato_data = {
    #             "fk_id_estudante": estudante_id,
    #             "fk_id_plano": fk_id_novo_plano,
    #             "fk_id_plano_personalizado": fk_id_plano_personalizado,
    #             "fk_id_adesao_plano": new_adesao.id_adesao_plano,
    #             "valor_final": valor_final,
    #             "data_inicio": data_adesao,
    #             "data_termino": data_validade_calc,
    #             "aulas_restantes": qtde_aulas,
    #             "status_contrato": "ativo"
    #         }
    #         contrato_model.insert_new_contrato(contrato_data)
        
    #     else:
    #          raise ValueError(f"Ação de plano '{acao.value}' inválida.")


    # async def handle_request_resolution(
    #     self, 
    #     id_solicitacao: int, 
    #     session_db: Session, 
    #     current_user: Dict[str, Any], 
    #     status_solicitacao: StatusSolcitacaoEnum, 
    #     agenda_repo: AgendaAulaRepository
    # ) -> SolicitacaoResponseSchema:
    #     UserValidation._check_admin_permission(current_user)

    #     solicitacao_model = SolicitacoesModel(session_db=session_db)
        
    #     # solicitacao_db:Optional[Solicitacoes] = solicitacao_model.select_solicitacao_by_id(id_solicitacao)
    #     # solicitacao_db = solicitacao_model.select_solicitacao_by_id(id_solicitacao)
    #     solicitacao_db: Optional[Solicitacoes] = await run_in_threadpool(
    #         solicitacao_model.select_solicitacao_by_id,
    #         id_solicitacao
    #     )
    #     if not solicitacao_db:
    #          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Solicitação ID {id_solicitacao} não encontrada.")
        
    #     if solicitacao_db.status_solicitacao in [StatusSolcitacaoEnum.ATENDIDA.value, StatusSolcitacaoEnum.RECUSADA.value]:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solicitação já foi processada.")

    #     aula_model = AulaModel(db_session=session_db) 
    #     adesao_plano_model = AdesaoPlanoModel(session_db=session_db)
        
    #     if status_solicitacao == StatusSolcitacaoEnum.ATENDIDA:
            
    #         if solicitacao_db.tipo_de_solicitacao == "aula":
    #             await self._process_aula_enrollment(
    #                 session_db, 
    #                 solicitacao_db, 
    #                 aula_model,
    #                 agenda_repo
    #             )
            
    #         elif solicitacao_db.tipo_de_solicitacao == "plano":
    #             # self._process_plano_subscribe(
    #             #     session_db, 
    #             #     solicitacao_db, 
    #             #     adesao_plano_model, 
    #             # )
    #             await run_in_threadpool(
    #                 self._process_plano_subscribe,
    #                 session_db,
    #                 solicitacao_db,
    #                 adesao_plano_model
    #             )
    #         else:
    #              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de solicitação desconhecido: {solicitacao_db.tipo_de_solicitacao}")

    #         # 4. Dados para Atualizar (ATENDIDA)
    #         update_data = SolicitacaoUpdate(
    #             status_solicitacao=StatusSolcitacaoEnum.ATENDIDA,
    #             data_resposta=datetime.now()
    #         )
        
    #     elif status_solicitacao == StatusSolcitacaoEnum.RECUSADA:
    #         # 4. Dados para Atualizar (RECUSADA)
    #         update_data = SolicitacaoUpdate(
    #             status_solicitacao=StatusSolcitacaoEnum.RECUSADA,
    #             data_resposta=datetime.now()
    #         )
    #     else:
    #          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status de resolução inválido.")

    #     # 5. Persiste a atualização e retorna
    #     # updated_solicitacao = solicitacao_model.update_solicitacao(id_solicitacao, update_data)
    #     updated_solicitacao = await run_in_threadpool(
    #         solicitacao_model.update_solicitacao,
    #         id_solicitacao,
    #         update_data
    #     )
    #     return SolicitacaoResponseSchema.model_validate(updated_solicitacao)


    # # --- MÉTODOS DE SUPORTE (Chamando as Models/Repos Diretamente) ---
    
    # async def _process_aula_enrollment(
    #     self, 
    #     session_db: Session, 
    #     solicitacao_db:Solicitacoes, 
    #     aula_model: AulaModel, 
    #     agenda_repo: AgendaAulaRepository
    # ):
    #     fk_id_aula = solicitacao_db.fk_id_aula_referencia 
    #     estudante_id = solicitacao_db.fk_id_estudante # Já estava correto
    #     # extra_info: Dict[str, Any] = solicitacao_db.extra_info
    #     # fk_id_aula = extra_info.get("fk_id_aula") 
    #     # estudante_id = solicitacao_db.fk_id_estudante

    #     if not fk_id_aula or not estudante_id:
    #         raise ValueError("Dados essenciais (aula/estudante ID) ausentes na solicitação.")

    #     matricula_dict = MatriculaCreate(fk_id_estudante=estudante_id).model_dump(exclude_none=True)
        
    #     try:
    #         await run_in_threadpool(
    #              aula_model.enroll_student, 
    #              fk_id_aula, 
    #              matricula_dict
    #          )
             
    #         await agenda_repo.add_participant(
    #              aula_id=fk_id_aula, 
    #              participant_id=estudante_id
    #          )
             
    #     except Exception as e:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Falha ao matricular na aula: {e}")


    # def _process_plano_subscribe(
    #     self, 
    #     session_db: Session, 
    #     solicitacao_db: Solicitacoes, 
    #     adesao_plano_model: AdesaoPlanoModel
    # ):        
    #     plano_model = PlanosModel(session_db=session_db)
        
    #     # extra_info: Dict[str, Any] = solicitacao_db.extra_info
    #     # fk_id_plano = extra_info.get("fk_id_plano_padrao") 
    #     # fk_id_plano_personalizado = extra_info.get("fk_id_plano_personalizado")
    #     # estudante_id = solicitacao_db.fk_id_estudante

    #     fk_id_plano = solicitacao_db.fk_id_novo_plano 
    #     fk_id_plano_personalizado = solicitacao_db.fk_id_novo_plano_personalizado
    #     estudante_id = solicitacao_db.fk_id_estudante # Já estava correto

    #     if not estudante_id or (not fk_id_plano and not fk_id_plano_personalizado):
    #         raise ValueError("Dados essenciais (estudante/plano ID) ausentes na solicitação.")

    #     tipo_plano = 'mensal'
    #     if fk_id_plano:
    #         plano_obj:Optional[Planos] = plano_model.select_plano_by_id(fk_id_plano)
    #         if not plano_obj:
    #              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plano Padrão com ID {fk_id_plano} não encontrado.")
    #         tipo_plano = plano_obj.tipo_plano.value
            
    #     data_adesao = datetime.now()
    #     # Lógica de cálculo de validade (semestral, trimestral, etc.)
    #     if tipo_plano == 'mensal':
    #         data_validade_calc = data_adesao + relativedelta(months=1)
    #     # ... (demais cálculos omitidos) ...
    #     else:
    #         data_validade_calc = data_adesao + relativedelta(months=1) 

    #     # 3. Construção dos dados para a Model de Adesão
    #     dados_para_model = {
    #         "fk_id_estudante": estudante_id,
    #         "fk_id_plano": fk_id_plano,
    #         "fk_id_plano_personalizado": fk_id_plano_personalizado,
    #         "data_validade": data_validade_calc
    #     }
        
    #     try:
    #         # CHAMA DIRETA À MODEL SQL
    #         new_adesao = adesao_plano_model.subscribe_plan(dados_para_model)
            
    #         if new_adesao is None:
    #              raise Exception("Falha na persistência no banco de dados.")

    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
    #             detail=f"Erro ao processar adesão: {e}"
    #         )





    # def update_request_status(self,id_solicitacao:int, session_db:Session, data_request:SolicitacaoUpdate, current_user: Dict[str, Any]):
    #     UserValidation._check_admin_permission(current_user)

    #     update_data: Dict[str, Any] = data_request.model_dump(by_alias=True, exclude_none=True)        
    #     if not update_data: 
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Nenhum campo fornecido para atualização."
    #         )
    #     novo_status = update_data.get('status_solicitacao')
    #     if novo_status in [StatusSolcitacaoEnum.ATENDIDA, StatusSolcitacaoEnum.RECUSADA]:
    #         update_data['data_resposta'] = datetime.now()
    #     updated_solicitacao_payload = SolicitacaoUpdate(**update_data)

    #     try:
    #         self.type_request = 'update_request_status'
    #         ValidarStatus.validar_status(session_db=session_db, id_solcitacao=id_solicitacao)    
    #         solicitacao_model = SolicitacoesModel(session_db=session_db)

    #         # self.updated_solicitacao = solicitacao_model.update_solicitacao(id_solcitacao=id_solicitacao, solicitacao_data=data_request)
    #         # if not self.updated_solicitacao:
    #         #     raise HTTPException(
    #         #         status_code=status.HTTP_404_NOT_FOUND,
    #         #         detail=f"Solicitação com ID {id_solicitacao} não encontrado."
    #         #     )
            
    #         # return SolicitacaoResponseSchema.model_validate(self.updated_solicitacao)

    #         updated_solicitacao_db = solicitacao_model.update_solicitacao(
    #             id_solcitacao=id_solicitacao, 
    #             solicitacao_data=updated_solicitacao_payload
    #         )
    #         if not updated_solicitacao_db:
    #             raise HTTPException(
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #                 detail=f"Solicitação com ID {id_solicitacao} não encontrado."
    #             )
            
    #         return SolicitacaoResponseSchema.model_validate(updated_solicitacao_db)
        

    #     except ValueError as err:
    #         raise HTTPException(
    #             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
    #             detail=f"Erro de validação dos dados: {err}" 
    #         )
    #     except Exception as err:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Falha ao processar solicitação: {err}"
    #         )
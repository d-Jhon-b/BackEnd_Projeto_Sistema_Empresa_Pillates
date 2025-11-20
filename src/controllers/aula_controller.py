from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from starlette.concurrency import run_in_threadpool

from datetime import datetime, date, timedelta
from src.model.AulaModel import AulaModel
from src.schemas.aulas_schemas import AulaResponse, AulaCreate, AulaUpdate, MatriculaCreate, AulaRecorrenteCreate

from src.controllers.utils.date_conversion import DateConverter
from src.controllers.validations.permissionValidation import UserValidation, NivelAcessoEnum 
from src.model.agendaModel.excecaoRepository import ExcecaoRepository 
from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse, AgendaAlunoUpdate

from src.model.AgendaModel import AgendaAulaRepository 
from src.schemas.agenda_schemas import AgendaAulaCreateSchema 


class AulaController:

    def get_aula_by_id(self, aula_id: int, current_user: dict, db_session: Session) -> AulaResponse:
        # lv_acesso = current_user.get('lv_acesso')
        # print(lv_acesso)
        # allowed_levels = [NivelAcessoEnum.ALUNO.value, NivelAcessoEnum.INSTRUTOR.value]
        # UserValidation._check_permission(current_user, allowed_levels)
        UserValidation._check_admin_permission(current_user=current_user)
        aula_model = AulaModel(db_session=db_session)
        aula = aula_model.select_aula_by_id(aula_id=aula_id) 

        if not aula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aula não encontrada."
            )
        return AulaResponse.model_validate(aula) # Converte ORM para Pydantic Response
    
    
    def get_all_aulas(self, studio_id: Optional[int], current_user: dict, db_session: Session) -> List[AulaResponse]:
        # Permissão: Qualquer usuário autenticado
        UserValidation._check_all_permission(current_user=current_user)
        user_estudio_id = current_user.get("fk_id_estudio")
        # for i in current_user.items():
        #     print(i)
        # if studio_id != None:
        #     studio_id = 

        if current_user.get("lv_acesso") != NivelAcessoEnum.SUPREMO.value:
            studio_id = user_estudio_id

        aula_model = AulaModel(db_session=db_session)
        aulas_from_db = aula_model.select_all_aulas(studio_id=studio_id)
        
        return [AulaResponse.model_validate(aula) for aula in aulas_from_db] # Converte ORM para Pydantic Response

    async def create_new_aula(self, aula_data: AulaCreate, current_user: dict, db_session: Session,agenda_repo: AgendaAulaRepository, excecao_repo: ExcecaoRepository) -> AulaResponse:
        UserValidation._check_admin_permission(current_user)
        aula_model = AulaModel(db_session=db_session)

        data_aula = aula_data.data_aula.date() 
        estudio_id = aula_data.fk_id_estudio

        excecoes_no_dia = await excecao_repo.find_excecoes_by_period(
            start_date=data_aula, 
            end_date=data_aula, 
            estudio_id=estudio_id
        )

        if excecoes_no_dia:
            # print(f'Errooo ao tentar inserir na data de aniversario\n\n\n\n')
            desc_excecao = excecoes_no_dia[0].get('descricao', 'Dia de folga ou fechamento.')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Não é possível agendar a aula. A data {data_aula} está marcada como exceção/indisponibilidade: {desc_excecao}"
            )

        estudantes_ids = aula_data.estudantes_a_matricular
        aula_dict = aula_data.model_dump(exclude={"estudantes_a_matricular"}, exclude_none=True)
        data_for_sql = aula_data.model_dump(
            exclude={
                "estudantes_a_matricular", 
                "disciplina",          
                "duracao_minutos"     
            }, 
            exclude_none=True
        )


        try:
            new_aula = await run_in_threadpool(
                aula_model.insert_new_aula, 
                data_for_sql, 
                estudantes_ids
            )
            
            agenda_create_schema = AgendaAulaCreateSchema(
                fk_id_aula=new_aula.id_aula, 
                fk_id_professor=new_aula.fk_id_professor,
                fk_id_estudio=new_aula.fk_id_estudio,
                data_aula=new_aula.data_aula, 
                desc_aula=new_aula.desc_aula, 
                
                disciplina=aula_data.disciplina,         
                duracao_minutos=aula_data.duracao_minutos, 
                
                participantes_ids=aula_data.estudantes_a_matricular,
            )
            
            await agenda_repo.create(agenda_create_schema) 
            
            return AulaResponse.model_validate(new_aula)
        
        except SQLAlchemyError as e:
            db_session.rollback() 
            print(f"ERRO DE PERSISTÊNCIA: {type(e).__name__}: {e}") 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar aula (verifique se as FKs de Estúdio/Professor são válidas).")
        except Exception as e:
            print(f"ERRO DE PERSISTÊNCIA: {type(e).__name__}: {e}")
            db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao agendar a aula: {e}. A aula no SQL foi revertida.")

    async def update_aula(self, aula_id: int, update_data: AulaUpdate, current_user: dict, db_session: Session, agenda_repo: AgendaAulaRepository) -> AulaResponse:
        UserValidation._check_admin_permission(current_user)
        aula_model = AulaModel(db_session=db_session)        
        update_dict = update_data.model_dump(exclude_none=True)
        updated_aula = await run_in_threadpool(aula_model.update_aula_data, aula_id, update_dict)
        
        if not updated_aula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula não encontrada para atualização.")
        try:
            await agenda_repo.update_by_aula_id(aula_id, update_dict)
        except Exception as e:
            print(f"ALERTA: Falha ao atualizar o MongoDB para aula {aula_id}: {e}")
            
        return AulaResponse.model_validate(updated_aula) 
    

    async def delete_aula_by_id_controller(self, aula_id: int, current_user: dict, db_session: Session, agenda_repo: AgendaAulaRepository):
        UserValidation._check_admin_permission(current_user)

        aula_model = AulaModel(db_session=db_session)
        
        deleted_sql = await run_in_threadpool(aula_model.delete_aula_by_id, aula_id)
        
        if not deleted_sql:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula não encontrada.")

        deleted_mongo = await agenda_repo.delete_by_aula_id(aula_id)        
        if not deleted_mongo:
           print(f"ALERTA: Aula {aula_id} deletada do SQL, mas não encontrada/deletada do MongoDB.")
            
        return {"message": "Aula excluída com sucesso de ambos os sistemas."}

    
    async def enroll_student_in_aula(self, aula_id: int, matricula_data: MatriculaCreate, current_user: dict, db_session: Session, agenda_repo: AgendaAulaRepository):
        # Permissão: Colaborador/Admin (quem faz a matrícula)
        UserValidation._check_admin_permission(current_user)

        aula_model = AulaModel(db_session=db_session)
        matricula_dict = matricula_data.model_dump(exclude_none=True)
        estudante_id = matricula_data.fk_id_estudante
        try:
            # aula_model.enroll_student(aula_id, matricula_dict)

            await run_in_threadpool(
                aula_model.enroll_student, 
                aula_id, 
                matricula_dict
            )
            update_mongo = await agenda_repo.add_participant(
                aula_id=aula_id, 
                participant_id=estudante_id
            )

            if not update_mongo:
                print(f"ALERTA: Estudante matriculado no SQL, mas falha ao encontrar/atualizar aula {aula_id} no MongoDB.") 
            return {"message": f"Estudante {estudante_id} matriculado na aula {aula_id} (SQL e MongoDB)."}
            # return {"message": f"Estudante {matricula_data.fk_id_estudante} matriculado na aula {aula_id}."}
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except SQLAlchemyError as e:
            print(f'{e}')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro na matrícula (verifique se o estudante/aula existem ou se já está matriculado).")
        
    async def create_aulas_recorrentes(
        self, 
        recorrencia_data: AulaRecorrenteCreate, 
        current_user: dict, 
        db_session: Session, 
        agenda_repo: AgendaAulaRepository, # Instância injetada
        excecao_repo: ExcecaoRepository, # Instância injetada
        agenda_aluno_repo: AgendaAlunoRepository # Instância injetada
    ) -> Dict[str, Any]:
        """
        Cria aulas recorrentes no SQL, Agenda do Estúdio (Mongo) e Agenda do Aluno (Mongo), 
        garantindo atomicidade no SQL.
        """
        
        UserValidation._check_admin_permission(current_user)
        # Instância do Modelo SQL, dependente da Session
        aula_model = AulaModel(db_session=db_session)

        # 1. Pré-processamento e Validação
        try:
            dia_alvo_num = DateConverter.get_weekday_index(recorrencia_data.dia_da_semana.value) 
            hora_inicio = datetime.strptime(recorrencia_data.horario_inicio, "%H:%M").time()
        except (ValueError, KeyError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro no formato de data/hora ou dia da semana. Detalhe: {e}")
        
        # 2. Busca exceções (Usando instância injetada)
        excecoes_db = await excecao_repo.find_excecoes_by_period(
            start_date=recorrencia_data.data_inicio_periodo, 
            end_date=recorrencia_data.data_fim_periodo, 
            estudio_id=recorrencia_data.fk_id_estudio
        )
        datas_excecao = {e["dataExcecao"].date() for e in excecoes_db}

        # 3. Gera as datas recorrentes válidas
        # ... (lógica de geração de datas_validas permanece a mesma) ...
        data_atual = recorrencia_data.data_inicio_periodo
        datas_validas = []
        while data_atual.weekday() != dia_alvo_num:
            data_atual += timedelta(days=1)
        while data_atual <= recorrencia_data.data_fim_periodo:
            if data_atual not in datas_excecao:
                data_completa = datetime.combine(data_atual, hora_inicio)
                datas_validas.append(data_completa)
            data_atual += timedelta(weeks=1) 
            
        if not datas_validas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma data de agendamento válida encontrada no período (verifique exceções ou datas)."
            )

        # 4. Loop de Criação e Transação
        aulas_criadas = []
        estudantes_ids = recorrencia_data.estudantes_a_matricular
        
        # Prepara dados base (Otimização)
        base_data_sql = recorrencia_data.model_dump(
            exclude={"dia_da_semana", "horario_inicio", "data_inicio_periodo", "data_fim_periodo", "estudantes_a_matricular", "capacidade_max", "disciplina", "duracao_minutos"}, 
            exclude_none=True
        )
        base_data_mongo = {
            "fk_id_professor": recorrencia_data.fk_id_professor,
            "fk_id_estudio": recorrencia_data.fk_id_estudio,
            "desc_aula": recorrencia_data.desc_aula,
            "disciplina": recorrencia_data.disciplina,
            "duracao_minutos": recorrencia_data.duracao_minutos,
            "participantes_ids": estudantes_ids,
        }
        
        try:
            for dt_completa in datas_validas:
                data_for_sql = {**base_data_sql, "data_aula": dt_completa}
                new_aula_sql = await run_in_threadpool(
                    aula_model.insert_new_aula, 
                    data_for_sql, 
                    estudantes_ids
                )
                
                agenda_create_schema = AgendaAulaCreateSchema(
                    fk_id_aula=new_aula_sql.id_aula, data_aula=dt_completa, **base_data_mongo
                )
                await agenda_repo.create(agenda_create_schema)

                for estudante_id in estudantes_ids:
                    aluno_agenda_data = AgendaAlunoCreate(
                        fk_id_estudante=estudante_id,
                        fk_id_aula_sql=new_aula_sql.id_aula,
                        fk_id_professor_sql=new_aula_sql.fk_id_professor,
                        data_hora_aula=dt_completa,
                        disciplina=recorrencia_data.disciplina,
                        fk_id_estudio=new_aula_sql.fk_id_estudio
                    )
                    await agenda_aluno_repo.create_registro(aluno_agenda_data)
                
                aulas_criadas.append(new_aula_sql.id_aula)
            
            # Commit da transação SQL
            await run_in_threadpool(db_session.commit)

        except SQLAlchemyError as e:
            await run_in_threadpool(db_session.rollback)
            print(f"ERRO SQL durante recorrência: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Falha de persistência ao agendar. Transação SQL revertida. Detalhe: {e}")
        except Exception as e:
            await run_in_threadpool(db_session.rollback)
            print(f"ERRO GERAL durante recorrência: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao agendar a recorrência. Transação SQL revertida. Detalhe: {e}")

        return {
            "message": f"{len(aulas_criadas)} aulas recorrentes criadas com sucesso para o período.",
            "aulas_ids": aulas_criadas,
            "datas_agendadas": [dt.strftime("%Y-%m-%d %H:%M") for dt in datas_validas]
        }


    
    # def create_new_aula(self, aula_data: AulaCreate, current_user: dict, db_session: Session) -> AulaResponse:
    #     # Permissão: Apenas Colaborador ou Supremo
    #     UserValidation._check_admin_permission(current_user)

    #     aula_model = AulaModel(db_session=db_session)
        
    #     estudantes_ids = aula_data.estudantes_a_matricular
    #     aula_dict = aula_data.model_dump(exclude={"estudantes_a_matricular"}, exclude_none=True)
        
    #     try:
    #         new_aula = aula_model.insert_new_aula(aula_dict, estudantes_ids)
    #         return AulaResponse.model_validate(new_aula) # Converte ORM para Pydantic Response
    #     except SQLAlchemyError as e:
    #         # Tratamento de erro específico do DB (ex: FK violada)
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar aula (verifique se as FKs de Estúdio/Professor são válidas).")

    
    # def update_aula(self, aula_id: int, update_data: AulaUpdate, current_user: dict, db_session: Session) -> AulaResponse:
    #     # Permissão: Apenas Colaborador ou Supremo
    #     UserValidation._check_admin_permission(current_user)

    #     aula_model = AulaModel(db_session=db_session)
        
    #     update_dict = update_data.model_dump(exclude_none=True)
        
    #     updated_aula = aula_model.update_aula_data(aula_id, update_dict)
        
    #     if not updated_aula:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula não encontrada para atualização.")
            
    #     return AulaResponse.model_validate(updated_aula) # Converte ORM para Pydantic Response
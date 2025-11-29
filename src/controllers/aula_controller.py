from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from starlette.concurrency import run_in_threadpool

from datetime import datetime, date, timedelta
from src.model.AulaModel import AulaModel
from src.schemas.aulas_schemas import AulaResponse, AulaCreate, AulaUpdate, MatriculaCreate, AulaRecorrenteCreate, MatriculaSeriesCreate

from src.controllers.utils.date_conversion import DateConverter
from src.controllers.validations.permissionValidation import UserValidation, NivelAcessoEnum 
from src.controllers.validations.enrollmentValidation import EnrollmentValidation 
from src.model.agendaModel.excecaoRepository import ExcecaoRepository 
from src.model.agendaAlunoModel.AgendaAlunoRepository import AgendaAlunoRepository
from src.schemas.agenda_aluno_schemas import AgendaAlunoCreate, AgendaAlunoResponse, AgendaAlunoUpdate
from src.repository.PlanoValidationRepository import PlanoValidationRepository

from src.model.AgendaModel import AgendaAulaRepository 
from src.schemas.agenda_schemas import AgendaAulaCreateSchema 
from src.controllers.agenda_aluno_controller import AgendaAlunoController 
import logging
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
        return AulaResponse.model_validate(aula) 
    
    
    def get_all_aulas(self, studio_id: Optional[int], current_user: dict, db_session: Session) -> List[AulaResponse]:
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
                tituloAulaCompleto=new_aula.titulo_aula,
                disciplina=aula_data.disciplina,         
                duracao_minutos=aula_data.duracao_minutos, 
                
                participantes_ids=aula_data.estudantes_a_matricular,
            )
            
            await agenda_repo.create(agenda_create_schema) 
            
            return AulaResponse.model_validate(new_aula)
        
        except SQLAlchemyError as e:
            db_session.rollback() 
            # print(f"ERRO DE PERSISTÊNCIA: {type(e).__name__}: {e}") 
            logging(f'{e}\n\n\n')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar aula (verifique se as FKs de Estúdio/Professor são válidas).")
        except Exception as e:
            # print(f"ERRO DE PERSISTÊNCIA: {type(e).__name__}: {e}")
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

    

    async def enroll_student_in_aula(self, aula_id: int, matricula_data: MatriculaCreate, current_user: dict, db_session: Session, 
            agenda_repo: AgendaAulaRepository,
            agenda_aluno_ctrl: 'AgendaAlunoController' 
        ):
        UserValidation._check_admin_permission(current_user)


        aula_model = AulaModel(db_session=db_session)
        matricula_dict = matricula_data.model_dump(exclude_none=True)
        estudante_id = matricula_data.fk_id_estudante
        tipo_de_aula = matricula_data.tipo_de_aula

        await EnrollmentValidation.validate_series_enrollment( 
            db_session=db_session, 
            estudante_id=estudante_id,
            num_aulas_na_serie=1
        )
        aula_mongo = await agenda_repo.get_by_aula_id(aula_id=aula_id)
        if not aula_mongo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Aula {aula_id} não encontrada na Agenda do Estúdio (MongoDB)."
            )
        

        try:
            await run_in_threadpool(
                aula_model.enroll_student, 
                aula_id, 
                matricula_dict
            )
            update_mongo = await agenda_repo.add_participant(
                aula_id=aula_id, 
                participant_id=estudante_id
            )
            registro_data = AgendaAlunoCreate(
                EstudanteID=estudante_id,
                AulaID=aula_id,
                ProfessorID=aula_mongo.get('professorResponsavel'), 
                DataHoraAula=aula_mongo.get('dataAgendaAula'),     
                disciplina=aula_mongo.get('disciplina'),           
                EstudioID=aula_mongo.get('EstudioID')              
            )
            await agenda_aluno_ctrl.create_registro(registro_data)

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
            if "duplicate key value" in str(e):
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estudante já está matriculado nesta aula.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro na matrícula (verifique se o estudante/aula existem ou se já está matriculado).")
        
    async def create_aulas_recorrentes(
        self, 
        recorrencia_data: AulaRecorrenteCreate, 
        current_user: dict, 
        db_session: Session, 
        agenda_repo: AgendaAulaRepository, 
        excecao_repo: ExcecaoRepository, 
        agenda_aluno_repo: AgendaAlunoRepository 
    ) -> Dict[str, Any]:
        """
        Cria aulas recorrentes no SQL, Agenda do Estúdio (Mongo) e Agenda do Aluno (Mongo), 
        garantindo atomicidade no SQL.
        """
        
        UserValidation._check_admin_permission(current_user)
        aula_model = AulaModel(db_session=db_session)

        try:
            dia_alvo_num = DateConverter.get_weekday_index(recorrencia_data.dia_da_semana.value) 
            hora_inicio = datetime.strptime(recorrencia_data.horario_inicio, "%H:%M").time()
        except (ValueError, KeyError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro no formato de data/hora ou dia da semana. Detalhe: {e}")
        
        excecoes_db = await excecao_repo.find_excecoes_by_period(
            start_date=recorrencia_data.data_inicio_periodo, 
            end_date=recorrencia_data.data_fim_periodo, 
            estudio_id=recorrencia_data.fk_id_estudio
        )
        datas_excecao = {e["dataExcecao"].date() for e in excecoes_db}

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

        aulas_criadas = []
        estudantes_ids = recorrencia_data.estudantes_a_matricular
        
        base_data_sql = recorrencia_data.model_dump(
            exclude={"dia_da_semana", "horario_inicio", "data_inicio_periodo", "data_fim_periodo", "estudantes_a_matricular", "disciplina", "duracao_minutos"}, 
            exclude_none=True
        )
        base_data_mongo = {
            "fk_id_professor": recorrencia_data.fk_id_professor,
            "fk_id_estudio": recorrencia_data.fk_id_estudio,
            "desc_aula": recorrencia_data.desc_aula,
            "titulo_aula": recorrencia_data.titulo_aula, 
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

                
                aulas_criadas.append(new_aula_sql.id_aula)
            
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


    async def enroll_student_in_series(
        self, 
        matricula_data: 'MatriculaSeriesCreate', # Usar aspas se o schema estiver no mesmo arquivo
        current_user: dict, 
        db_session: Session, 
        agenda_repo: AgendaAulaRepository,
        agenda_aluno_ctrl: 'AgendaAlunoController' # Injete o Controller
    ):
        UserValidation._check_admin_permission(current_user)

        aula_model = AulaModel(db_session=db_session)

        estudante_id = matricula_data.fk_id_estudante
        titulo_aula = matricula_data.titulo_aula
        tipo_de_aula = matricula_data.tipo_de_aula

        try:
            aulas_series = await agenda_repo.find_future_aulas_by_titulo(titulo_aula=titulo_aula)

            if not aulas_series:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nenhuma aula futura encontrada para a série: {titulo_aula}"
                )

            num_aulas_na_serie = len(aulas_series)
            
            # logging.info(f"Estudante {estudante_id}, Saldo Restante: 4 (Confirmado).")
            # logging.info(f" Aulas Futuras (Calculadas): 0 (Confirmado).")
            # logging.info(f"CRÍTICO: Série '{titulo_aula}' tem {num_aulas_na_serie} aulas.")
        
            saldo_disponivel =await EnrollmentValidation.validate_series_enrollment( 
                db_session=db_session, 
                estudante_id=estudante_id,
                num_aulas_na_serie=num_aulas_na_serie
            )
            aulas_a_matricular = min(num_aulas_na_serie, saldo_disponivel)
            
            aulas_para_processar = aulas_series[:aulas_a_matricular]
            import logging
            logging.info(f"DEBUG: Série tem {num_aulas_na_serie} aulas. Saldo: {saldo_disponivel}. Matricular: {aulas_a_matricular}")
            matriculas_efetuadas = 0


            for aula_mongo in aulas_para_processar:
                aula_sql_id = aula_mongo.get('AulaID')

                matricula_dict = {
                "fk_id_estudante": estudante_id,
                "tipo_de_aula": tipo_de_aula
                }

                try:
                    await run_in_threadpool(
                        aula_model.enroll_student, 
                        aula_sql_id, 
                        matricula_dict
                    )

                    await agenda_repo.add_participant(
                        aula_id=aula_sql_id, 
                        participant_id=estudante_id
                    )

                    registro_data = AgendaAlunoCreate(
                        EstudanteID=estudante_id,
                        AulaID=aula_sql_id,
                        ProfessorID=aula_mongo.get('professorResponsavel'),
                        DataHoraAula=aula_mongo.get('dataAgendaAula'),
                        # 'disciplina' ou 'titulo_aula' do Mongo para o registro
                        disciplina=aula_mongo.get('disciplina') or titulo_aula, 
                        EstudioID=aula_mongo.get('EstudioID')
                    )

                    await agenda_aluno_ctrl.create_registro(registro_data)

                    matriculas_efetuadas += 1

                except ValueError as e:
                    print(f"Aviso: Aula {aula_sql_id} atingiu limite. Pulando. Detalhe: {e}")
                    continue
                except SQLAlchemyError as e:
                        if "duplicate key value" in str(e):
                            print(f"Aviso: Aluno {estudante_id} já matriculado na aula SQL {aula_sql_id}. Pulando.")
                            continue
                        raise e
            
            
            if matriculas_efetuadas < num_aulas_na_serie:
                 return {
                    "message": f"Estudante matriculado em {matriculas_efetuadas} de {num_aulas_na_serie} aulas da série '{titulo_aula}' (limite atingido pelo saldo).",
                    "aulas_nao_matriculadas": num_aulas_na_serie - matriculas_efetuadas
                 }
            # if matriculas_efetuadas == 0:
            #     return {"message": f"Estudante {estudante_id} já está matriculado em todas as aulas futuras da série '{titulo_aula}' ou todas atingiram o limite."}

            return {"message": f"Estudante {estudante_id} matriculado em {matriculas_efetuadas} aulas futuras da série '{titulo_aula}' (SQL, MongoDB e Agenda de Aluno criada)."}
        except HTTPException:
            raise
        except Exception as e:
            print(f"Erro geral na matrícula em série: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao matricular em série de aulas.")


    async def unenroll_student_from_aula(
        self, 
        aula_id: int, 
        estudante_id: int, 
        current_user: dict, 
        db_session: Session, 
        agenda_repo: AgendaAulaRepository,
        agenda_aluno_repo: AgendaAlunoRepository 
    ) -> Dict[str, Any]:

        UserValidation._check_admin_permission(current_user)

        aula_model = AulaModel(db_session=db_session)
        
        deleted_sql = await run_in_threadpool(
            aula_model.unenroll_student, 
            aula_id, 
            estudante_id
        )
        
        if not deleted_sql:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Matrícula do Estudante {estudante_id} na Aula {aula_id} não encontrada no SQL."
            )

       
        
        mongo_updated = await agenda_repo.remove_participant(
            aula_id=aula_id, 
            participant_id=estudante_id
        )

        if not mongo_updated:
            logging.warning(f"ALERTA: Estudante desmatriculado do SQL, mas ID {estudante_id} não encontrado no array 'participantes' da Aula {aula_id} no MongoDB (Agenda Estúdio).")


        deleted_aluno_agenda = await agenda_aluno_repo.delete_registro_by_estudante_and_aula(
            estudante_id=estudante_id,
            aula_id=aula_id
        )
        
        if not deleted_aluno_agenda:
            logging.warning(f"ALERTA: Registro individual do estudante {estudante_id} para Aula {aula_id} não encontrado/deletado no MongoDB (Agenda Aluno).")


        return {
            "message": f"Estudante {estudante_id} desmatriculado da Aula {aula_id} com sucesso.",
            "status_sql": "Sucesso",
            "status_mongo_estudio": "Sucesso (removido do array participantes)" if mongo_updated else "Alerta (não encontrado no array participantes)",
            "status_mongo_aluno": "Sucesso (registro individual deletado)" if deleted_aluno_agenda else "Alerta (registro individual não encontrado)"
        }
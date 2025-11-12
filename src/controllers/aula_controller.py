from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from starlette.concurrency import run_in_threadpool # Adicionar esta importação


from src.model.AulaModel import AulaModel
from src.schemas.aulas_schemas import AulaResponse, AulaCreate, AulaUpdate, MatriculaCreate
from src.controllers.validations.permissionValidation import UserValidation, NivelAcessoEnum # Reutilizando sua validação
from src.model.agendaModel.excecaoRepository import ExcecaoRepository 

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
        
        user_estudio_id = current_user.get("fk_id_estudio")
        
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
        



    
    # def create_new_aula(self, aula_data: AulaCreate, current_user: dict, db_session: Session) -> AulaResponse:
    #     # Permissão: Apenas Colaborador ou Supremo
    #     UserValidation._check_admin_permission(current_user)

    #     aula_model = AulaModel(db_session=db_session)
        
    #     # 1. Extrai dados do Pydantic para o Model
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
        
    #     # 1. Converte o Pydantic para Dict (o Model só precisa de um Dict de atualização)
    #     update_dict = update_data.model_dump(exclude_none=True)
        
    #     updated_aula = aula_model.update_aula_data(aula_id, update_dict)
        
    #     if not updated_aula:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula não encontrada para atualização.")
            
    #     return AulaResponse.model_validate(updated_aula) # Converte ORM para Pydantic Response
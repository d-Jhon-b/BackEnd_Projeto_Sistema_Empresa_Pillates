from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from typing import List

# Importar Repositórios e Modelos necessários
from src.repository.ContratoRepository import ContratoRepository 
from src.model.AulaModel import AulaModel 

class EnrollmentValidation:
    @staticmethod
    async def validate_series_enrollment(
        db_session: Session,
        estudante_id: int, 
        num_aulas_na_serie: int
    ) -> bool:

        contrato_repo = ContratoRepository(db_session=db_session)
        aula_model = AulaModel(db_session=db_session)
        
        aulas_restantes = await run_in_threadpool(
            contrato_repo.get_aulas_restantes_by_estudante, 
            estudante_id
        )

        if aulas_restantes <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Matrícula negada. Estudante {estudante_id} não possui saldo de aulas ou contrato ativo."
            )

        aulas_futuras_matriculadas = await run_in_threadpool(
            aula_model.count_future_enrollments, 
            estudante_id
        )

        saldo_disponivel = aulas_restantes - aulas_futuras_matriculadas
        
        # if num_aulas_na_serie > saldo_disponivel:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=(f"Matrícula em série negada. O aluno possui **{aulas_restantes}** aulas "
        #                 f"restantes e já está matriculado em **{aulas_futuras_matriculadas}** aulas futuras. "
        #                 f"Saldo disponível para novas matrículas: **{saldo_disponivel}**. "
        #                 f"A série solicitada tem **{num_aulas_na_serie}** aulas.")
        #     )

        return saldo_disponivel
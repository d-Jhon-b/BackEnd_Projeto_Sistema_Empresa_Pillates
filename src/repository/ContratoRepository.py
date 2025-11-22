from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

from src.model.planosModel.contratoConfig import Contrato # Assumindo que Contrato tem um campo 'aulas_restantes'
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.userModel.typeUser.aluno import Estudante_Aula
from src.model.userModel.userConfig import Usuario
from src.model.PlanosCustomizadosModel import PlanosPersonalizados
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.model.planosModel.planoConfig import Planos
# from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano

class ContratoRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def _get_active_contract(self, estudante_id: int) -> Optional[Contrato]:
        """Busca o contrato ativo principal para o estudante."""
        # A lógica real pode ser mais complexa (validade, tipo, prioridade), mas simplificamos:
        stmt = select(Contrato).join(AdesaoPlano).where(
            and_(
                AdesaoPlano.fk_id_estudante == estudante_id,
                Contrato.status_contrato == 'ativo', 
            )
        ).order_by(Contrato.data_inicio.desc())
        
        return self.session.execute(stmt).scalar_one_or_none()

    def get_aulas_restantes_by_estudante(self, estudante_id: int) -> int:
        contrato = self._get_active_contract(estudante_id)
        
        if not contrato:
            return 0 
            
        return contrato.aulas_restantes
    

    def debitar_aula_do_plano(self, estudante_id: int) -> bool: 

        contrato: Optional[Contrato] = None 
        try:
            contrato = self._get_active_contract(estudante_id)

            if not contrato:
                raise ValueError(f"Estudante {estudante_id} não possui contrato ativo para débito.")

            if contrato.aulas_restantes <= 0:
                raise ValueError(f"Contrato ID {contrato.id_contrato} não tem saldo de aulas restante (Saldo: {contrato.aulas_restantes}).")
            
            update_stmt = (
                update(Contrato)
                .where(Contrato.id_contrato == contrato.id_contrato)
                .values(aulas_restantes=Contrato.aulas_restantes - 1)
            )
            
            self.session.execute(update_stmt)
            self.session.commit()
            
            logging.info(f"Débito: 1 aula consumida. Estudante {estudante_id}. Contrato ID: {contrato.id_contrato}")
            return True
            
        except ValueError:
            self.session.rollback() 
            raise 
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"Erro SQL ao debitar aula do plano: {e}")
            raise 
            
        except Exception as e:
            self.session.rollback()
            raise e
        


# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.database.connPostGreNeon import CreateSessionPostGre
# def test_get_aulas_restantes_by_estudante():
    

#     try:
#         create_session = CreateSessionPostGre()
#         db_session = create_session.get_session()
#         repo = ContratoRepository(db_session)
        
#         # Substitua 1 pelo ID de um estudante que TEM aulas restantes (Ex: 10)
#         ID_ESTUDANTE_COM_AULAS = 1 
        
#         # Substitua 99 pelo ID de um estudante que NÃO TEM contrato ativo (Ex: 99)
#         ID_ESTUDANTE_SEM_CONTRATO = 99 

#         # --- Teste 1: Estudante com aulas ativas ---
#         aulas_1 = repo.get_aulas_restantes_by_estudante(ID_ESTUDANTE_COM_AULAS)
#         print(f"Estudante {ID_ESTUDANTE_COM_AULAS} tem {aulas_1} aulas restantes.")
        
#         if aulas_1 > 0:
#             print("Resultado OK: Contrato Ativo e saldo > 0.")
#         else:
#             print(f"ATENÇÃO: Esperava-se saldo > 0. O saldo atual é {aulas_1}.")
            
#         # --- Teste 2: Estudante sem contrato ativo ---
#         aulas_2 = repo.get_aulas_restantes_by_estudante(ID_ESTUDANTE_SEM_CONTRATO)
#         print(f"Estudante {ID_ESTUDANTE_SEM_CONTRATO} tem {aulas_2} aulas restantes.")
        
#         if aulas_2 == 0:
#             print("Resultado OK: Contrato Inativo/Inexistente retorna 0.")
#         else:
#             print(f"ERRO DE LÓGICA: Esperava-se 0. Retornou {aulas_2}.")

#     except Exception as e:
#         print(f"ERRO INESPERADO no teste do ContratoRepository: {e}")
#     finally:
#         if 'db_session' in locals():
#             db_session.close()

# if __name__ == "__main__":
#     test_get_aulas_restantes_by_estudante()
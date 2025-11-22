from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.model.AlunoModel import AlunoModel
from src.model.userModel.typeUser.aluno import Estudante
from src.controllers.validations.permissionValidation import UserValidation


class TargetUserFinder:

    @staticmethod
    def check_and_get_target_user_id(
        session_db: Session, 
        estudante_id: int, 
        current_user: Dict[str, Any]
    ) -> int:

        estudante_model = AlunoModel(db_session=session_db)
        target_user_id = estudante_model.select_id_user_by_fk_id_estudante(estudante_id)
        
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Estudante ID {estudante_id} não encontrado ou sem usuário associado."
            )
            
        UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
        return target_user_id
    

    @staticmethod
    def check_and_get_target_user_id_all_users(
        session_db: Session, 
        estudante_id: int, 
        current_user: Dict[str, Any]
    ) -> int:
  
        estudante_model = AlunoModel(db_session=session_db)
        target_user_id = estudante_model.select_id_user_by_fk_id_estudante(estudante_id) 
        
        if target_user_id is None: # Use 'is None' pois 0 ou outros IDs são possíveis, embora improvável
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Estudante ID {estudante_id} não encontrado."
            )
            
        # Aplica a validação de permissão estendida (Admin/Colaborador/Instrutor OU Dono)
        UserValidation.check_self_or_admin_permission(
            current_user=current_user, 
            target_user_id=target_user_id
        )
        
        return target_user_id
    

    @staticmethod
    def check_id_estudante_by_id_user(
        session_db: Session, 
        user_id: int, 
    ) -> int:
  
        estudante_model = AlunoModel(db_session=session_db)
        target_user_id = estudante_model.select_student_by_id(user_id=user_id) 
        if target_user_id is None: # Use 'is None' pois 0 ou outros IDs são possíveis, embora improvável
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Estudante ID {target_user_id} não encontrado."
            )
        id_estundate=target_user_id.estudante.id_estudante
        print(id_estundate)
            
      
        return id_estundate
    # @staticmethod
    # def check_estudante_id(
    #     current_user:Dict[str, Any],
    #     estudante_model:AlunoModel
    # )->int:
        
    #     user_id = current_user.get("id_user")
    #     # user_id = current_user.get("id_user")
    #     target_estudante_id= estudante_model.select_student_by_id(user_id=user_id)
    #     if not target_estudante_id:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, 
    #             detail=f"Estudante ID {target_estudante_id} não encontrado ou sem usuário associado."
    #         )
        
    #     target_user_id = target_estudante_id.estudante.fk_id_user
    #     UserValidation.check_self_or_admin_permission(current_user=current_user, target_user_id=target_user_id)
    #     # print(target_user_id)
    #     return target_estudante_id.estudante.id_estudante
    # def check_and_get_estudante_user_id(session_db:Session, user_id)

# from src.database.connPostGreNeon import CreateSessionPostGre
# from src.model.AlunoModel import AlunoModel

# create_session=CreateSessionPostGre()
# session = create_session.get_session()
# aluno_model = AlunoModel(db_session=session)
# id_estudante = TargetUserFinder.check_estudante_id(3,aluno_model)
# print(id_estudante)
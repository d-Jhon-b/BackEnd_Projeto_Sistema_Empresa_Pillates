from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel

from src.model.AlunoModel import AlunoModel

from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import (UserResponse, LoginRequestSchema, NivelAcessoEnum, 
AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload,
AlunoUpdatePayload
)
from src.controllers.validations.permissionValidation import UserValidation


from src.controllers.operations.operations import Operations

class AlunoController:
    def create_aluno(self, payload: AlunoCreatePayload, current_user: dict, db_session: Session):
        UserValidation._check_admin_permission(current_user)
        
        user_data_dict = payload.user_data.model_dump()
        if payload.senha_user:
            password_to_use = payload.senha_user
        else:
            password_to_use = payload.user_data.num_doc_user
        
        user_data_dict['senha_user'] = password_to_use
        user_data_dict['lv_acesso'] = NivelAcessoEnum.ALUNO
        
        endereco_data_dict = payload.endereco_data.model_dump() if payload.endereco_data else None
        contato_data_dict = payload.contato_data.model_dump() if payload.contato_data else None
        extra_data_dict = payload.extra_data.model_dump()

        return Operations._execute_creation(db_session, user_data_dict, endereco_data_dict, contato_data_dict, extra_data_dict)

    def select_all_aluno_controller(self, studio_id: int | None, current_user: dict, db_session: Session):
        UserValidation._check_admin_permission(current_user)

        user_model = AlunoModel(db_session=db_session)
        users_from_db = user_model.select_all_students(studio_id=studio_id)
        return [UserResponse.model_validate(user) for user in users_from_db]
    
    def select_aluno_by_id(self, user_id: int, current_user: dict, db_session: Session):
        UserValidation.check_self_or_admin_permission(current_user, user_id)

        user_model = AlunoModel(db_session=db_session)
        user = user_model.select_student_by_id(user_id=user_id) 

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        return UserResponse.model_validate(user)
    
    def update_aluno_data(self, user_id: int, update_data: AlunoUpdatePayload, current_user: dict, db_session: Session) -> UserResponse:
        UserValidation.check_self_or_admin_permission(current_user, user_id)
        user_model = UserModel(db_session=db_session)

        raw_data = update_data.model_dump(exclude_unset=True, exclude_none=True)
        
        endereco_data = raw_data.pop('endereco', None)
        contatos_data = raw_data.pop('contatos', None)
        aluno_extra_data = raw_data.pop('extra_aluno', None) 
        
        updated_user = user_model.update_user_data(
            user_id=user_id,
            user_data_to_update=raw_data, 
            endereco_data_to_update=endereco_data,
            contato_data_to_update=contatos_data,
            extra_data_to_update=aluno_extra_data
        )

        if not updated_user:
             raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado ou erro na atualização.")
             
        return UserResponse.model_validate(updated_user)
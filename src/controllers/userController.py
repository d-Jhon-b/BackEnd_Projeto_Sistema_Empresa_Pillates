from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import UserResponse, LoginRequestSchema, NivelAcessoEnum, AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload
from src.controllers.validations.permissionValidation import UserValidation

from src.controllers.operations.operations import Operations

class UserController:
    def login_for_access_token(self, payload: LoginRequestSchema, db_session: Session):
        user_data_dict = {'email_user': payload.email, 'senha_user': payload.password}
        user_model = UserModel(db_session=db_session)
        user = user_model.login_user(user_data=user_data_dict)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos.")

        token_data = {"id_user": user.id_user, "lv_acesso": user.lv_acesso}
        access_token = auth_manager.create_access_token(data=token_data)
        return {"access_token": access_token, "token_type": "bearer"}       

    
    def get_user_by_id(self, user_id: int, current_user: dict, db_session: Session):
        UserValidation.check_self_or_admin_permission(current_user, user_id)

        # requester_id = current_user.get("id_user")
        # requester_level = current_user.get("lv_acesso")
        user_model = UserModel(db_session=db_session)
        user = user_model.select_user_id(user_id=user_id) 

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        return UserResponse.model_validate(user)
    
    def get_all_users(self, studio_id: int | None, current_user: dict, db_session: Session):
        UserValidation._check_admin_permission(current_user)

        user_model = UserModel(db_session=db_session)
        users_from_db = user_model.select_all_users(studio_id=studio_id)
        return [UserResponse.model_validate(user) for user in users_from_db]

        


    def delete_user_by_id_controller(self, current_user:dict , user_id:int, db_session:Session):
        UserValidation._check_admin_permission(current_user)

        # requester_id = current_user.get("id_user")
        user_model=UserModel(db_session=db_session)
        deleted = user_model.delete_user_by_id(user_id=user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        print(f'Usuário excluído com sucesso.')
        return 
    
        
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import UserResponse, LoginRequestSchema, NivelAcessoEnum, AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload
from src.controllers.validations.permissionValidation import UserValidation


class UserController:
    # def login_for_access_token(self, payload: LoginRequestSchema, db_session: Session):
    #     user_data_dict = {'email_user': payload.email, 'senha_user': payload.password}
    #     user_model = UserModel(db_session=db_session)
    #     user = user_model.login_user(user_data=user_data_dict)

    #     if not user:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos.")

    #     token_data = {"id_user": user.id_user, "lv_acesso": user.lv_acesso}
    #     access_token = auth_manager.create_access_token(data=token_data)
    #     return {"access_token": access_token, "token_type": "bearer"}       

    # def _execute_creation(self, db_session: Session, user_data: dict, endereco_data: dict, contato_data: dict, extra_data: dict):
    #     user_model = UserModel(db_session=db_session)
    #     novo_usuario = user_model.create_new_user(
    #         user_data=user_data,
    #         endereco_data=endereco_data,
    #         contato_data=contato_data,
    #         extra_data=extra_data
    #     )
    #     if not novo_usuario:
    #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível criar o usuário. O e-mail ou documento já pode existir.")
    #     return UserResponse.model_validate(novo_usuario)
    
    # def get_user_by_id(self, user_id: int, current_user: dict, db_session: Session):
    #     UserValidation._check_admin_permission(current_user)
    #     requester_id = current_user.get("id_user")
    #     requester_level = current_user.get("lv_acesso")

    #     is_admin = requester_level in [NivelAcessoEnum.SUPREMO.value, NivelAcessoEnum.COLABORADOR.value]
    #     is_requesting_self = requester_id == user_id
    #     if not (is_admin or is_requesting_self):
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Você não tem permissão para visualizar este usuário."
    #         )

    #     user_model = UserModel(db_session=db_session)
    #     user = user_model.select_user_id(user_id=user_id) 

    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Usuário não encontrado."
    #         )
    #     return UserResponse.model_validate(user)
    
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

        
    # def create_aluno(self, payload: AlunoCreatePayload, current_user: dict, db_session: Session):
    #     UserValidation._check_admin_permission(current_user)
        
    #     user_data_dict = payload.user_data.model_dump()
    #     user_data_dict['senha_user'] = payload.senha_user
    #     user_data_dict['lv_acesso'] = NivelAcessoEnum.ALUNO
        
    #     endereco_data_dict = payload.endereco_data.model_dump() if payload.endereco_data else None
    #     contato_data_dict = payload.contato_data.model_dump() if payload.contato_data else None
    #     extra_data_dict = payload.extra_data.model_dump()

    #     return self._execute_creation(db_session, user_data_dict, endereco_data_dict, contato_data_dict, extra_data_dict)

    # def create_instrutor(self, payload: InstrutorCreatePayload, current_user: dict, db_session: Session):
    #     UserValidation._check_admin_permission(current_user)

    #     user_data_dict = payload.user_data.model_dump()
    #     user_data_dict['senha_user'] = payload.senha_user
    #     user_data_dict['lv_acesso'] = NivelAcessoEnum.INSTRUTOR
        
    #     endereco_data_dict = payload.endereco_data.model_dump() if payload.endereco_data else None
    #     contato_data_dict = payload.contato_data.model_dump() if payload.contato_data else None
    #     extra_data_dict = {
    #         "tipo_especializacao": payload.tipo_especializacao.value,
    #         "numero_de_registro": payload.numero_de_registro, 
    #         "formacao": payload.formacao,                 
    #         "data_contratacao": payload.data_contratacao      
    #     }

    #     return self._execute_creation(db_session, user_data_dict, endereco_data_dict, contato_data_dict, extra_data_dict)

    # def create_colaborador(self, payload: ColaboradorCreatePayload, current_user: dict, db_session: Session):
    #     UserValidation._check_admin_permission(current_user)

    #     user_data_dict = payload.user_data.model_dump()
    #     user_data_dict['senha_user'] = payload.senha_user
    #     user_data_dict['lv_acesso'] = NivelAcessoEnum.COLABORADOR
        
    #     endereco_data_dict = payload.endereco_data.model_dump() if payload.endereco_data else None
    #     contato_data_dict = payload.contato_data.model_dump() if payload.contato_data else None
    #     extra_data_dict = {"is_recepcionista": payload.is_recepcionista}

    #     return self._execute_creation(db_session, user_data_dict, endereco_data_dict, contato_data_dict, extra_data_dict)


    # ------ Métodos de Delete ---

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
    
        
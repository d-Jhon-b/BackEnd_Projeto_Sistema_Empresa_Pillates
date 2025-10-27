from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import UserResponse, LoginRequestSchema, NivelAcessoEnum, AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload
from src.controllers.validations.permissionValidation import UserValidation

class Operations:
    @staticmethod
    def _execute_creation(db_session: Session, user_data: dict, endereco_data: dict, contato_data: dict, extra_data: dict):
            user_model = UserModel(db_session=db_session)
            novo_usuario = user_model.create_new_user(
                user_data=user_data,
                endereco_data=endereco_data,
                contato_data=contato_data,
                extra_data=extra_data
            )
            if not novo_usuario:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível criar o usuário. O e-mail ou documento já pode existir.")
            return UserResponse.model_validate(novo_usuario)
        
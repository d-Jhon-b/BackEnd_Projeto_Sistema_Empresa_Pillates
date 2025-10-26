from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import UserResponse, LoginRequestSchema, NivelAcessoEnum, AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload
from src.controllers.validations.permissionValidation import UserValidation

from src.controllers.operations.operations import Operations

class ColaboradoreController:
    def create_colaborador(self, payload: ColaboradorCreatePayload, current_user: dict, db_session: Session):
        UserValidation._check_admin_permission(current_user)

        user_data_dict = payload.user_data.model_dump()
        user_data_dict['senha_user'] = payload.senha_user
        user_data_dict['lv_acesso'] = NivelAcessoEnum.COLABORADOR
        
        endereco_data_dict = payload.endereco_data.model_dump() if payload.endereco_data else None
        contato_data_dict = payload.contato_data.model_dump() if payload.contato_data else None
        extra_data_dict = {"is_recepcionista": payload.is_recepcionista}

        return Operations._execute_creation(db_session, user_data_dict, endereco_data_dict, contato_data_dict, extra_data_dict)
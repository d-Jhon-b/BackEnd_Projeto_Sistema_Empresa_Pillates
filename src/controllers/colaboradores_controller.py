from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Optional, Any, List
# from src.model.UserModel import UserModel
from src.model.ColaboradorModel import ColaboradorModel

from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import UserResponse, LoginRequestSchema, NivelAcessoEnum, AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload
from src.controllers.validations.permissionValidation import UserValidation

from src.controllers.operations.operations import Operations

class ColaboradoreController:
    def create_colaborador(self, payload: ColaboradorCreatePayload, current_user: dict, db_session: Session):
        UserValidation._check_admin_permission(current_user)

        user_data_dict = payload.user_data.model_dump()

        if payload.senha_user: #verifica se o valor da senha existe
            password_to_use = payload.senha_user #se sim, passa o valor para a criação da conta
        else:
            password_to_use = payload.user_data.num_doc_user #se não, passa o valor do documento para a criação da conta

        user_data_dict['senha_user'] = password_to_use
        user_data_dict['lv_acesso'] = NivelAcessoEnum.COLABORADOR
        
        endereco_data_dict = payload.endereco_data.model_dump() if payload.endereco_data else None
        contato_data_dict = payload.contato_data.model_dump() if payload.contato_data else None
        extra_data_dict = {"is_recepcionista": payload.is_recepcionista}

        return Operations._execute_creation(db_session, user_data_dict, endereco_data_dict, contato_data_dict, extra_data_dict)
    
    def select_all_colaboradores_controller(self, studio_id: Optional[int], current_user: Dict[str, Any], db_session: Session) -> List[UserResponse]:
        UserValidation._check_admin_permission(current_user)

        colaborador_model = ColaboradorModel(db_session=db_session)
        users_from_db = colaborador_model.select_all_colaboradores(studio_id=studio_id)
        
        return [UserResponse.model_validate(user) for user in users_from_db]

    def select_colaborador_by_id_controller(self, user_id: int, current_user: dict, db_session: Session) -> UserResponse:
        UserValidation.check_self_or_admin_permission(current_user, user_id) 

        colaborador_model = ColaboradorModel(db_session=db_session)
        user = colaborador_model.select_colaborador_by_id(user_id=user_id) 

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Colaborador não encontrado ou ID inválido."
            )

        return UserResponse.model_validate(user)
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.model.UserModel import UserModel
from src.utils.authUtils import auth_manager
from src.schemas.user_schemas import UserResponse, LoginRequestSchema, NivelAcessoEnum, AlunoCreatePayload, InstrutorCreatePayload, ColaboradorCreatePayload


class UserValidation():
    @staticmethod
    def _check_permission( current_user: dict, allowed_levels: list):
        creator_level = current_user.get("lv_acesso")
        if NivelAcessoEnum.SUPREMO.value not in allowed_levels:
             allowed_levels.append(NivelAcessoEnum.SUPREMO.value)
             
        if creator_level not in allowed_levels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para esta ação."
            )
    @staticmethod
    def _check_admin_permission( current_user: dict):
        allowed_levels = [
            NivelAcessoEnum.COLABORADOR.value
        ]
        UserValidation._check_permission(current_user, allowed_levels)
    @staticmethod
    def _check_instrutor_permission( current_user: dict):
        allowed_levels = [
            NivelAcessoEnum.INSTRUTOR.value,
            NivelAcessoEnum.COLABORADOR.value 
        ]
        UserValidation._check_permission(current_user, allowed_levels)
    
    @staticmethod
    def _check_aluno_permission( current_user: dict):
        allowed_levels = [
            NivelAcessoEnum.ALUNO.value
        ]
        UserValidation._check_permission(current_user, allowed_levels)

    @staticmethod
    def check_self_or_admin_permission(current_user: dict, target_user_id: int):
        requester_id = current_user.get("id_user")
        requester_level = current_user.get("lv_acesso")
        is_admin = requester_level in [
            NivelAcessoEnum.SUPREMO.value, 
            NivelAcessoEnum.COLABORADOR.value
        ]
        is_requesting_self = (requester_id == target_user_id)

        if not (is_admin or is_requesting_self):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para visualizar este usuário."
            )
from fastapi import HTTPException, status
from src.schemas.user_schemas import UserCreatePayload
from src.model.UserModel import UserModel

class UserController:
    def create_user(self, payload: UserCreatePayload):
        """
        Orquestra a criação de um novo usuário.
        """
        # Desmonta o payload para o formato que o UserModel espera
        # O .dict() converte o modelo Pydantic para um dicionário Python
        user_data_dict = payload.user_data.dict()
        user_data_dict['senha_user'] = payload.senha_user

        endereco_data_dict = payload.endereco_data.dict() if payload.endereco_data else None
        contato_data_dict = payload.contato_data.dict() if payload.contato_data else None
        extra_data_dict = payload.extra_data.dict() if payload.extra_data else None

        # Instancia o Model. A permissão 'supremo' permite criar qualquer usuário.
        # Em um sistema real, isso viria de um token de autenticação.
        user_model = UserModel(tipoUser='supremo')

        # Chama o método do Model para criar o usuário
        novo_usuario = user_model.create_new_user(
            user_data=user_data_dict,
            endereco_data=endereco_data_dict,
            contato_data=contato_data_dict,
            extra_data=extra_data_dict
        )

        # Se o Model retornar None, significa que algo deu errado (ex: e-mail duplicado)
        if not novo_usuario:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # 409 Conflict é bom para duplicatas
                detail="Não foi possível criar o usuário. O e-mail ou documento já pode existir."
            )

        return novo_usuario
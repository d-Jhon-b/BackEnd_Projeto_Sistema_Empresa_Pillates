# src/services/authService.py

from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

# Importa o UserModel que você acabou de editar
from src.model.UserModel import UserModel 
# Importa os schemas que criamos anteriormente
from src.schemas.user_schemas import LoginRequestSchema, ForgotPasswordSchema, ResetPasswordSchema
# Importa seu gerenciador de token
from src.utils.authUtils import auth_manager 
# Importa sua classe de HASH
from src.model.utils.HashPassword import HashPassword 
# Importa o serviço de e-mail (dos Passos 2 e 3)
from src.services.emailService import EmailService 
from pydantic import EmailStr

class AuthService:
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_model = UserModel(db_session)
        # (Assumindo que o EmailService foi criado nos passos anteriores)
        self.email_service = EmailService() 

    def login_for_access_token(self, payload: LoginRequestSchema):
        """
        [LÓGICA MOVIDA DO USERCONTROLLER]
        Chama o método login_user (otimizado) do UserModel.
        """
        user_data_dict = {'email_user': payload.email, 'senha_user': payload.password}
        
        user = self.user_model.login_user(user_data=user_data_dict)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Email ou senha incorretos."
            )

        token_data = {"id_user": user.id_user, "lv_acesso": user.lv_acesso}
        access_token = auth_manager.create_access_token(data=token_data)
        
        return {"access_token": access_token, "token_type": "bearer"}

    async def forgot_password(
        self, 
        payload: ForgotPasswordSchema, 
        background_tasks: BackgroundTasks
    ):
        """
        [LÓGICA NOVA]
        Usa o método 'select_user_by_email' que você adicionou.
        """
        user = self.user_model.select_user_by_email(email=payload.email)
        
        if not user:
            logging.warning(f"Tentativa de redefinição p/ e-mail não cadastrado: {payload.email}")
            return {"message": "Se um usuário com este e-mail existir, um link será enviado."}

        #Cria o token de reset
        expires_delta = timedelta(minutes=15)
        reset_data = {"sub": user.email_user, "scope": "password_reset"}
        reset_token = auth_manager.create_access_token(data=reset_data, expires_delta=expires_delta)

        #Envia o e-mail (usa o EmailService do Passo 3)
        background_tasks.add_task(
            self.email_service.send_password_reset_email,
            email_to=user.email_user,
            token=reset_token,
            username=user.name_user
        )
        
        return {"message": "Se um usuário com este e-mail existir, um link será enviado."}

    def reset_password(self, payload: ResetPasswordSchema):
        """
        [LÓGICA NOVA]
        Usa HashPassword e o novo 'update_user_password'.
        """
        token_payload = auth_manager.decode_access_token(payload.token)
        if not token_payload:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado.")
            
        email: EmailStr = token_payload.get("sub")
        scope: str = token_payload.get("scope")
        
        if not email or scope != "password_reset":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido (escopo incorreto).")
            
        user = self.user_model.select_user_by_email(email=email)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário do token não encontrado.")
            
        # Cria o novo hash 
        hash_bytes = HashPassword.hash_password(payload.new_password)
        hash_str = hash_bytes.decode('utf-8')
        #Atualiza no banco (usa o novo método do Passo 5)
        success = self.user_model.update_user_password(
            user_id=user.id_user,
            hashed_password_str=hash_str
        )
        
        if not success:
             raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Não foi possível atualizar a senha.")
            
        return {"message": "Senha atualizada com sucesso."}
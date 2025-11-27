# src/services/emailService.py
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
import logging
from src.database.envConfig.envEmail import EnvLoaderEmail
from fastapi import HTTPException, status

class EmailService:
    _fm: FastMail = None 

    def __init__(self):
        if EmailService._fm is None:
            try:
                conf = EnvLoaderEmail().get_config()
                EmailService._fm = FastMail(conf)
            except Exception as e:
                logging.error(f"Falha ao inicializar o serviço de e-mail: {e}")

    async def send_password_reset_email(self, email_to: EmailStr, token: str, username: str):
        if EmailService._fm is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Serviço de e-mail não configurado.")

        reset_link = f"http://localhost:5173/new-password?token={token}"

        html_content = f"""
        <p>Olá, {username},</p>
        <p>Clique no link para redefinir sua senha: 
           <a href="{reset_link}">Redefinir Senha</a> (Link expira em 15 minutos)</p>
        """
        message = MessageSchema(
            subject="Redefinição de Senha",
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )
        try:
            await EmailService._fm.send_message(message)
            logging.info(f"E-mail de redefinição de senha enviado para {email_to}")
        except Exception as e:
            logging.error(f"FALHA CRÍTICA AO ENVIAR E-MAIL para {email_to}: {e}")
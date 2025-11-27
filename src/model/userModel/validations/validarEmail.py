from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from src.model.userModel.userConfig import Usuario
from sqlalchemy.orm import Session

class ValidarEmail():
    @staticmethod
    def validar_email(session, email:str):
        stmt = select(Usuario).where(Usuario.email_user == email) 
        res = session.execute(stmt).scalar_one_or_none()
        if res:
            print('Usuario já cadastrado')
            return True
        # print(f'Usuario não cadastrado FDP')
        return False
        
        
        # if res:
        #     # print('teste')
        #     print('Usuário com esse email já existe:')
        #     return False
        # return True

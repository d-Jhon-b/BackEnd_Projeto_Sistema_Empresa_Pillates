from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from src.model.userModel.userConfig import Usuario

from src.database.connPostGreNeon import CreateSessionPostGre


from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from src.model.userModel.userConfig import Usuario

from typing import Optional, Dict, Union


createSession = CreateSessionPostGre()
session = createSession.get_session()



class ValidarSenha():
    @staticmethod
    def validar_senha(session, email:str)->Optional[str]:
        stmt = select(Usuario.senha_user).where(Usuario.email_user == email) 
        storege_password = session.execute(stmt).scalar_one_or_none()
        return storege_password
    

    
        # print(res)
        # if res:
        #     # print('teste')
        #     print('Usuário com esse email já existe:')
        #     return str(res)
        # return None

# validate = ValidarSenha.validar_senha(session, 'tiocatador@gmail.com')
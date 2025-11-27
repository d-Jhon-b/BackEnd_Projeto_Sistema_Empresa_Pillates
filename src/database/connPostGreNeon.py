from typing import Optional, Dict, Union

from sqlalchemy import create_engine, text, select, func, URL, Engine
from sqlalchemy.orm import create_session, Session


from src.database.modelConfig.configPostGre import PostGreParamBuilder



class CreateSessionPostGre():
    def __init__(self):

        self.env_data = PostGreParamBuilder()
        self.engine = None
        self.session = None
        self.url_neon = None
        try:
            self.url_neon = self.env_data.build_url_env()
        except Exception as err:
            print(f'erro ao buscar dados da url ou url expirada: {err}')


    def get_engine(self)->Optional[Engine]:
        if self.engine is not None:
            return self.engine
        if not self.url_neon:
            print(f'URL de conxão não disponivel')
        try:
            self.engine = create_engine(self.url_neon,echo=True,pool_pre_ping=True)
            with self.engine.connect() as conn:
                conn.execute(text('select 1'))
            print('Conexão com PostGreSQl (NEON) estabelecida')
            return self.engine
        except Exception as err:
            print(f'Erro ao criar o Engine ou conector: {err}')
            self.engine = None
            return None

    def get_session(self) ->Optional[Session]:
        self.engine = self.get_engine()
        if self.engine is None:
            return None       
        return Session(bind=self.engine)
    

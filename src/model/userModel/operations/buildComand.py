from pydantic import BaseModel
from typing import Optional, Dict,Union,Any, Tuple
from psycopg2 import sql    


class BuildComand():
    tipoOperacao:str
    values:str
    def __init__(self, tipoOperacao:str):
        self.tipoOperacao = tipoOperacao



    def build_comand(self, nomeTabela:str, **data)->Optional[Tuple[sql.Composed, Tuple]]:
        self.nomeTabela = nomeTabela
        self.data = data
        match self.tipoOperacao:
            case 'insert':
                for self.chave, self.valor in data.items():
                    print(f'{self.chave}: {self.valor}')
                # try:
                #     self.nomeTabela = nomeTabela
                #     self.comand = f"""
                #     insert into {self.nomeTabela}(name_user, foto_user, nasc_user, tipo_doc_user, num_doc_user, lv_acesso)
                #     values({data['name_user'], data['foto_user'], data['nasc_user'], data['tipo_doc_user'], data['num_doc_user'],data['lv_acesso']})
                #     """
                #     return self.comand
                # except:
                #     return f'Erro ao acessar'
            case 'update':
                return
            case 'delete':
                return
            case 'select':
                return
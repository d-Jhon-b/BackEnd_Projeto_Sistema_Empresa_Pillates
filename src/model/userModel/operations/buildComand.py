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
        self.columns = data.keys()
        self.valores = data.values()
        match self.tipoOperacao:
            case 'insert':
                # for self.chave, self.valor in data.items():
                #     print(f'{self.chave}: {self.valor}')
                self.columnNames =', '.join(self.columns)
                self.placeholderValues = ','.join(['%s'] * len(self.columns))
                try:
                    print(self.columnNames)
                    print(self.placeholderValues)
                    self.comand_str = f"""
                    insert into {self.nomeTabela}({self.columnNames})
                    values({self.placeholderValues})
                    """
                    return self.comand_str, tuple(self.valores)
                except Exception as e:
                    print(f'Erro ao construir comando: {e}')
                    return None
                
            case 'update':
                return
            case 'delete':
                return
            case 'select':
                return
            case _:
                print(f'Operação {self.tipoOperacao} invalido')
                return None
            


# data = {'name_user': 'jhon', 
#         'foto_user': None,
#         'nasc_user': '2005-05-03',
#         'tipo_doc_user': 'cpf',
#         'num_doc_user': '42502556899',
#         'lv_acesso':'supremo'
        
#         }
# typeOperation = 'INSERT'.lower()
# objBUildComand= BuildComand(typeOperation)
# buildComand = objBUildComand.build_comand('usuario', **data)
# print(buildComand)
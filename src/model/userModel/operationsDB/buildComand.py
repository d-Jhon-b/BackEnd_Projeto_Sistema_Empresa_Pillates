from pydantic import BaseModel
from typing import Optional, Dict,Union,Any, Tuple, Sequence
from psycopg2 import sql    

ComandResult = Optional[Tuple[str, Tuple[Any, ...]]]

class BuildComand():
    tipoOperacao:str
    values:str
    def __init__(self, tipoOperacao:str):
        self.tipoOperacao = tipoOperacao



        # Inicializando atributos para evitar AttributeError
        self.nomeTabela = ""
        self.columns_list = "*"
        self.condition_str = None
        self.join_clause_str = None
        self.condition_values_tuple = ()
        self.data_dict = {}


    def build_comand(self, nomeTabela: str, 
        columns: Union[str, Sequence[str]] = '*', 
        condition: Optional[str] = None, 
        join_clause: Optional[str] = None,
        condition_values: Sequence[Any] = (),
        **data:Any
        
        )->Optional[Tuple[sql.Composed, Tuple]]:


        self.nomeTabela = nomeTabela
        self.columns_list = columns
        self.condition_str = condition
        self.join_clause_str = join_clause
        self.condition_values_tuple = condition_values
        self.data_dict = data
        
        # Inicializa as variáveis que guardarão o comando final
        self.command_str: str = ""
        self.final_values: Tuple[Any, ...] = ()



        match self.tipoOperacao:
            case 'insert':
                if not self.data_dict:
                    print("Erro: Nenhum dado fornecido para INSERT.")
                    return None
                    
                self.columns_keys = self.data_dict.keys()
                self.valores = self.data_dict.values()
                
                self.columnNames = ', '.join(self.columns_keys)
                self.placeholderValues = ','.join(['%s'] * len(self.columns_keys))
                
                self.command_str = f"""
                INSERT INTO {self.nomeTabela} ({self.columnNames})
                VALUES ({self.placeholderValues})
                """
                self.final_values = tuple(self.valores)
                return self.command_str, self.final_values

            case 'select':
                
                if isinstance(self.columns_list, str):
                    self.columnNames = self.columns_list
                else:
                    self.columnNames = ', '.join(self.columns_list)
                    
                self.from_clause = f"FROM {self.nomeTabela}"
                if self.join_clause_str:
                    self.from_clause += f" {self.join_clause_str}"
                
                self.where_clause = ""
                if self.condition_str:
                    self.where_clause = f"WHERE {self.condition_str}"
                
                self.command_str = f"SELECT {self.columnNames} {self.from_clause} {self.where_clause}"
                
                self.final_values = tuple(self.condition_values_tuple)
                return self.command_str, self.final_values
            case 'update':
                return
            case 'delete':
                return
            
            


#antigo modelo de insert:
 # self.columnNames =', '.join(self.columns)
                # self.placeholderValues = ','.join(['%s'] * len(self.columns))
                # try:
                #     # print(self.columnNames)
                #     # print(self.placeholderValues)

                #     self.comand_str = f"""
                #     insert into {self.nomeTabela}({self.columnNames})
                #     values({self.placeholderValues})
                #     """
                #     return self.comand_str, tuple(self.valores)
                # except Exception as e:
                #     print(f'Erro ao construir comando: {e}')
                #     return None
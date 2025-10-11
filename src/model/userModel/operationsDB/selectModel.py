from typing import Optional, Union, Dict, List, Sequence, Any


from src.database.connPostGre import PostGreModel
from src.model.userModel.operationsDB.buildComand import BuildComand


class SelectValues():
    def __init__(self):
        self.TipoOperacao = 'select'
        print(f'tipo de operação: {self.TipoOperacao}')
        try:
            self.buildComandInstance = BuildComand(self.TipoOperacao.lower())
        except:
            raise

    def select(
            self, 
            nome_tabela: str, 
            columns: Union[str, Sequence[str]] = '*', 
            condition: Optional[str] = None, 
            join_clause: Optional[str] = None,
            condition_values: Sequence[Any] = ()
        ) -> Optional[List[Dict[str, Any]]]:        
        
        self.postGre = PostGreModel()
        self.conn = self.postGre.connect_db()
        if isinstance(self.conn, str):
            print(f'erro na conexão ao banco: {self.conn}')
            return
        self.cursor=self.conn.cursor()

        # self.nomeTabela = nomeTabela
        # self.data = data

        self.comandTurple = self.buildComandInstance.build_comand(
                nomeTabela=nome_tabela,
                columns=columns,
                condition=condition,
                join_clause=join_clause,
                condition_values=condition_values
            )
        try: 
            if self.comandTurple is None:
                print('Erro: Comando não construído ou operador não suportado')
                return None
                
            self.command_str, self.values = self.comandTurple
            
            self.cursor.execute(self.command_str, self.values)

            # Processar os resultados (Busca de dados)
            column_names = [desc[0] for desc in self.cursor.description]
            records = self.cursor.fetchall()
            
            result = []
            for record in records:
                result.append(dict(zip(column_names, record)))

            print(f'Comando : \n{self.command_str} \nexecutado')
            
            #self.conn.commit()
            
            return result
        except Exception as e:
            print(f'erro ao chamar build_comadn: {e}')
            return None
        finally:
            self.postGre.diconnect_db()



# objSelectValue = SelectValues()
# res = objSelectValue.select(
#     'usuario', 
#     ['id_user', 'nasc_user'], 
#     "id_user <= %s", 
#     None,            
#     (7,)        
# )

# print(res)
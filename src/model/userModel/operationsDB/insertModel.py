#from sqlalchemy.orm import sessionmaker
from typing import Optional, Union, Dict

from src.database.connPostGre import PostGreModel
from src.model.userModel.operationsDB.buildComand import BuildComand

class InsertValues():
    def __init__(self):

        self.TipoOperacao = 'insert'  # Agora é fixo e interno
        print(f'tipo de operação: {self.TipoOperacao}')
        try:
            self.buildComandInstance = BuildComand(self.TipoOperacao.lower())
        except:
            raise    

    def insert(self, nomeTabela, **data)->Optional[str]:
        self.postGre = PostGreModel()
        self.conn = self.postGre.connect_db()
        if isinstance(self.conn, str):
            print(f'erro de conexão: {self.conn}')
            return
        self.cursor = self.conn.cursor()
        
        self.nomeTabela = nomeTabela
        self.data= data
        
        try:
            self.comandTurple = self.buildComandInstance.build_comand(self.nomeTabela, **self.data) 
            if self.comandTurple is None:
                print("Erro: Comando não construído ou operação não suportada.")
                return None
            self.command_str, self.values = self.comandTurple 
            self.cursor.execute(self.command_str, self.values)

            print(f'Comando : \n{self.command_str} \nexecutado')


            # inserted_id = self.cursor.fetchone()[0]
            # self.conn.commit()
            # return inserted_id

            if self.nomeTabela == 'usuario':
                # Isso só funcionará se BuildComand adicionar 'RETURNING id_user_post_gre'
                inserted_id = self.cursor.fetchone()[0]
                self.conn.commit()
                return inserted_id
            else:
                # Para tabelas de detalhes, apenas commit e retorna True para sucesso.
                self.conn.commit()
                return True
        except Exception as e:
            print(f'erro ao chamar build_comadn: {e}')
            self.conn.rollback() 
            return None
        finally:
            self.postGre.diconnect_db()
            


# print(f'teste')
# try:
# insertTeste = InsertValues('insert')
# data = {
#     'name_user':'Jorge Pneu', 
#     'foto_user':'', 
#     'nasc_user':'20225-09-09', 
#     'tipo_doc_user':'cnpj', 
#     'num_doc_user':'22345678911', 
#     'lv_acesso':'colaborador'
# }
# insertRes = insertTeste.insert('usuario', **data)
# print(insertRes)
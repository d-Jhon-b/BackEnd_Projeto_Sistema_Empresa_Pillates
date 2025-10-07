#from sqlalchemy.orm import sessionmaker
from typing import Optional, Union

from src.database.connPostGre import PostGreModel
from src.model.userModel.operations.buildComand import BuildComand

class InsertValues():
    def __init__(self, TipoOperacao = 'insert'):
        self.TipoOperacao = TipoOperacao
        
        print(f'tipo de operação: {self.TipoOperacao}')
        try:
            self.buildComandInstance = BuildComand(TipoOperacao.lower())
        except Exception as e: 
            print(f"Erro ao inicializar BuildComand: {e}")
            self.buildComandInstance = None   

    def insert(self,nomeTabela, **data)->Optional[str]:
        self.postGre = PostGreModel()
        self.conn = self.postGre.connect_db()
        if isinstance(self.conn, str):
            print(f'erro de conexão: {self.conn}')
            return None
        self.cursor = self.conn.cursor()
        self.nomeTabela = nomeTabela
        self.data = data
        
        try:
            self.comandTurple = self.buildComandInstance.build_comand(self.nomeTabela, **self.data) 
            if self.comandTurple is None:
                print("Erro: Comando não construído ou operação não suportada.")
                return None
            self.command_str, self.values = self.comandTurple 
            self.cursor.execute(self.command_str, self.values)

            print(f'Comando : \n{self.command_str} \nexecutado')
            self.conn.commit()
            return 'Sucesso'
        except Exception as e:
            print(f'erro ao chamar build_comadn: {e}')
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
#     'num_doc_user':'12345678911', 
#     'lv_acesso':'colaborador'
# }
# insertRes = insertTeste.insert('usuario', **data)
# print(insertRes)
    # postGre = PostGreModel()
    # conn = postGre.connect_db()
    # cursor = conn.cursor()
    # cursor.execute('select *from usuario')
    # res = cursor.fetchall()
    # print(res)

# except: 
#     f'erro ao inserrir XD'
#from sqlalchemy.orm import sessionmaker

from src.database.connPostGre import PostGreModel
from src.model.userModel.operations.buildComand import BuildComand

class InsertValues():
    def __init__(self, TipoOperacao = 'insert'):
        self.TipoOperacao = TipoOperacao
        
        print(f'tipo de operação: {self.TipoOperacao}')

        
        try:
            self.buildComandInstance = BuildComand(TipoOperacao.lower())
        except:
            return    

    def insert(self,nomeTabela, **data):
        postGre = PostGreModel()
        conn = postGre.connect_db()
        if isinstance(conn, str):
            print(f'erro de conexão: {conn}')
            return
        cursor = conn.cursor()
        
        self.nomeTabela = nomeTabela
        self.data= data
        
        try:
            self.buildComand = self.buildComandInstance.build_comand(self.nomeTabela, **self.data) 
            # buildComand = BuildComand.build_comand('')
            return self.buildComand
        except Exception as e:
            print(f'erro ao chamar build_comadn: {e}')
            return None


# print(f'teste')
# try:
insertTeste = InsertValues('insert')
insertRes = insertTeste.insert('usuario', name_user='Jorge Pneu', foto_user=None, nasc_user='20225-09-09', tipo_doc_user='cnpj', num_doc_user='12345678911', lv_acesso='colaborador')
print(insertRes)
    # postGre = PostGreModel()
    # conn = postGre.connect_db()
    # cursor = conn.cursor()
    # cursor.execute('select *from usuario')
    # res = cursor.fetchall()
    # print(res)

# except: 
#     f'erro ao inserrir XD'
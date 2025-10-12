# src/model/configModel/operations/selectModel.py (Trecho a adicionar)
from typing import Dict, Any, Optional
import psycopg2 
import logging

from src.model.configModel.userSettings.valuesUser import NivelAcessoEnum 
# from src.dat.database.connPostGre import PostGreModel # Sua importação de conexão
from src.database.connPostGre import PostGreModel

# Configuração básica de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



class SelectValues:

    def selecionar_por_email(self, email: str) -> Optional[Dict[str, Any]]:        
        self.postGre = PostGreModel()
        self.conn = self.postGre.connect_db()
        if self.conn is None:
            logging.error("Falha ao conectar ao banco de dados para busca de login.")
            return None
            
        cursor = None
        try:
            cursor = self.conn.cursor()
            
            comand = """
            SELECT senha_user, lv_acesso, id_user, name_user
            FROM usuario
            WHERE email_user = %s;
            """
            
            cursor.execute(comand, (email,))
            resultado = cursor.fetchone()
            
            if resultado:
                hash_limpo = resultado[0].strip() # hash limpo, o banco de dados estava cortando o hash... não pergunte pq

                return {
                    'senha_user': hash_limpo,  
                    'lv_acesso': resultado[1],  
                    'id_user': resultado[2],
                    'name_user': resultado[3],
                }
            return None 

        except psycopg2.Error as db_error:
            logging.error(f"ERRO DE DB na busca de login: {db_error}")
            return None
        finally:
            self.postGre.diconnect_db()


# if __name__ == "__main__":
#     EMAIL_EXISTENTE = 'maria.aluna@teste.com'
#     EMAIL_INEXISTENTE = 'naoexiste@teste.com'
#     selector = SelectValues()
#     resultado_existente = selector.selecionar_por_email(EMAIL_EXISTENTE)
    
#     if resultado_existente:
#         print(f"ID: {resultado_existente.get('id_user')}")
#         print(f"Nível: {resultado_existente.get('lv_acesso')}")
#         print(f"Hash (Parcial): {resultado_existente.get('senha_user', '')[:10]}...")
#     else:
#         print(f"FALHA: Usuário {EMAIL_EXISTENTE} não encontrado. Verifique seu DB.")
        
#     resultado_inexistente = selector.selecionar_por_email(EMAIL_INEXISTENTE)
    
#     if resultado_inexistente is None:
#         print("Sucesso")
#     else:
#         print("FALHA")
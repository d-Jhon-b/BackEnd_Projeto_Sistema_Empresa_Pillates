# import psycopg2
# from psycopg2 import OperationalError


# try:
#     conn=psycopg2.connect(
#         dbname="SIG_PILLATES_DB",
#         user="postgres",
#         password="962266514",
#         host="localhost",
#         port="5432"
#     )
#     cursor = conn.cursor()
#     print('conexão bem-sucedida')
#     cursor.execute('select version();')
#     db_version=cursor.fetchall()
#     print(f'versão do postgreSQL:\n{db_version}')
# except OperationalError as err:
#     print(f'erro ao conectar ao banco de dados:\n{err}')

# finally:
#     if 'cursor' in locals() and cursor:
#         cursor.close
#     if 'conexao' in locals() and conn:
#         conn.close()
#     print('conexão com postgreSQL foi encerrada')


from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Carregar as variáveis do .env
load_dotenv()

# Obter URI do MongoDB
uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Criar cliente e conectar
client = MongoClient(uri)

# Acessar um banco (cria automaticamente se não existir)
db = client["meu_banco"]

# Acessar uma coleção
collection = db["minha_colecao"]

# Inserir um documento (exempo)
collection.insert_one({"nome": "João", "idade": 30})

# Buscar e imprimir documentos
for doc in collection.find():
    print(doc)

# Encerrar conexão (opcional, mas recomendado)
client.close()
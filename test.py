# # test_connection.py

# import asyncio
# from sqlalchemy.future import select

# # Importa o conector e a função para obter a sessão
# from src.database.connPostGre import POSTGRE_DB_CONNECTOR, get_postgre_session

# # Importa o modelo que queremos testar
# from src.model.userModel import Usuario

# async def test_database_connection():
#     """
#     Um script simples para configurar o engine, conectar ao banco
#     e fazer uma consulta na tabela de usuários.
#     """
#     print("--- Iniciando teste de conexão e ORM ---")
    
#     # É crucial configurar o engine antes de tentar obter uma sessão
#     POSTGRE_DB_CONNECTOR.setup_engine()

#     try:
#         # Pega uma sessão do banco de dados usando nosso gerenciador de contexto
#         async with get_postgre_session() as session:
#             print("\n[SUCESSO] Sessão com o banco de dados obtida.")

#             # Cria uma consulta simples para selecionar o primeiro usuário da tabela
#             query = select(Usuario).limit(1)
            
#             # Executa a consulta
#             result = await session.execute(query)
            
#             # Pega o primeiro objeto do resultado
#             user = result.scalars().first()

#             if user:
#                 print("[SUCESSO] Consulta realizada. Primeiro usuário encontrado:")
#                 # O __repr__ que definimos no modelo será usado aqui
#                 print(f"   -> {user}")
#             else:
#                 print("[AVISO] Tabela 'usuario' está vazia, mas a conexão e o modelo estão funcionando!")

#     except Exception as e:
#         print(f"\n[ERRO] Ocorreu um problema durante o teste: {e}")
    
#     finally:
#         # Garante que o pool de conexões será encerrado no final
#         await POSTGRE_DB_CONNECTOR.disconnect_db()
#         print("\n--- Teste finalizado ---")


# # Roda a função de teste assíncrona
# if __name__ == "__main__":
#     asyncio.run(test_database_connection())
from src.database.connPostGreNeon import CreateSessionPostGre

def get_db():
    """
    Função de dependência do FastAPI para obter uma sessão de banco de dados.
    Usa 'yield' para garantir que a sessão seja fechada após a requisição.
    """
    db_session_creator = CreateSessionPostGre()
    session = db_session_creator.get_session()
    try:
        yield session # 1. Fornece a sessão para o endpoint
    finally:
        session.close() # 3. Fecha a sessão DEPOIS que a resposta foi enviada
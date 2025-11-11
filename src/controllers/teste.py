# import asyncio
# from unittest.mock import AsyncMock, MagicMock, patch, Mock
# from datetime import datetime
# from fastapi import HTTPException # Importar HTTPException para possíveis asserts de erro

# # 🚨 Ajuste os caminhos de importação conforme sua estrutura de pastas
# # Assumindo que este teste está rodando em um arquivo separado e precisa importar o controller e schemas
# from src.controllers.aula_controller import AulaController
# from src.controllers.validations.permissionValidation import NivelAcessoEnum
# # Importe as classes Pydantic reais do seu projeto
# from src.schemas.aulas_schemas import AulaCreate, AulaResponse 


# # --- 1. MOCKS DE DADOS ---
# MOCK_AULA_ID = 1
# MOCK_FK_PROFESSOR = 1
# TITULO_DA_AULA = "Pilates Avançado"
# MOCK_DATA_AULA = datetime(2026, 1, 15, 18, 0, 0)
# MOCK_DESC = "Aula de alto nível."
# MOCK_PARTICIPANTES = [2, 3]
# MOCK_FK_ESTUDIO = 1 # Adicionado para completar o mock
# MOCK_DISCIPLINA = "Pilates Clássico"
# MOCK_DURACAO = 60

# # Simula o objeto ORM retornado pelo 'insert_new_aula'
# mock_new_aula_sql = Mock(
#     id_aula=MOCK_AULA_ID,
#     data_aula=MOCK_DATA_AULA,
#     fk_id_professor=MOCK_FK_PROFESSOR,
#     fk_id_estudio=MOCK_FK_ESTUDIO,
#     titulo_aula=TITULO_DA_AULA,
#     desc_aula=MOCK_DESC,
    
#     # 🚨 CAMPOS FALTANTES ADICIONADOS AQUI:
#     fk_id_professor_substituto=None, # Deve ser None para passar na validação Optional[int]
#     # O Pydantic espera uma lista vazia ou de objetos EstudanteAulaResponse.
#     # Uma lista vazia [] é o valor mais seguro para um teste isolado.
#     estudantes_associacao=[], 
# )

# # Simula a classe Pydantic AulaCreate (Input)
# class MockAulaCreate: 
#     # Atributos de entrada
#     fk_id_professor=MOCK_FK_PROFESSOR
#     titulo_aula=TITULO_DA_AULA
#     fk_id_estudio=MOCK_FK_ESTUDIO
#     disciplina=MOCK_DISCIPLINA
#     data_aula=MOCK_DATA_AULA
#     duracao_minutos=MOCK_DURACAO
#     desc_aula=MOCK_DESC
#     estudantes_a_matricular=MOCK_PARTICIPANTES
    
#     # Simula o método do Pydantic que o Controller usa
#     def model_dump(self, exclude, exclude_none):
#          return {
#              "fk_id_professor": self.fk_id_professor,
#              "titulo_aula": self.titulo_aula,
#              "fk_id_estudio": self.fk_id_estudio,
#              "data_aula": self.data_aula,
#              "desc_aula": self.desc_aula
#          }
# # --- Fim MOCKS ---


# async def test_create_new_aula_sql_success_isolated():
#     """ 
#     Testa o cenário de sucesso do create_new_aula, garantindo que o retorno 
#     do run_in_threadpool seja processado corretamente.
#     """
#     print("\n--- INICIANDO TESTE: create_new_aula (SQL ISOLADO) ---")
    
#     # 1. Mocks de Dependências
#     mock_db_session = MagicMock()
#     mock_agenda_repo = AsyncMock() # Continua mockado, mas assert_not_called será usado
#     mock_controller = AulaController()
    
#     mock_aula_create_data = MockAulaCreate()
#     mock_current_user = {"lv_acesso": NivelAcessoEnum.COLABORADOR.value}

#     # 2. Patch do run_in_threadpool: Simula a chamada ao Model no PostgreSQL
#     # Garante que 'new_aula' dentro do controller receba mock_new_aula_sql
#     with patch('src.controllers.aula_controller.run_in_threadpool', 
#                new_callable=AsyncMock, 
#                return_value=mock_new_aula_sql) as mock_run_threadpool:

#         # O AulaModel ainda é instanciado no Controller, então é bom mocká-lo também
#         # with patch('src.controllers.aula_controller.AulaModel') as mock_aula_model_cls:
            
#             # --- Execução do Controller ---
#         try:
#             result = await mock_controller.create_new_aula(
#                 aula_data=mock_aula_create_data,
#                 current_user=mock_current_user,
#                 db_session=mock_db_session,
#                 agenda_repo=mock_agenda_repo
#             )
#         except Exception as e:
#             print(f"❌ Erro na Execução do Controller: {type(e).__name__}: {e}")
#             raise e
        
#         # --- 3. ASSERTs ---

#         # A) Verifica se a chamada do Model foi simulada
#         mock_run_threadpool.assert_called_once()
        
#         # B) Verifica se a parte do MongoDB não foi chamada (devido ao código comentado)
#         # mock_agenda_repo.create.assert_not_called()
#         mock_agenda_repo.create.assert_called_once()
#         # C) Verifica se a resposta final (AulaResponse) está correta
#         assert result.id_aula == MOCK_AULA_ID
#         assert result.titulo_aula == TITULO_DA_AULA
        
#         print(f"✅ Sucesso! Aula {result.id_aula} retornada após inserção mockada no SQL.")

# # --- Rodar o teste (Execução Simples) ---
# if __name__ == '__main__':
#     try:
#         asyncio.run(test_create_new_aula_sql_success_isolated())
#     except AssertionError as e:
#         print(f"❌ Teste Falhou no Assert: {e}")
#     except Exception as e:
#         print(f"❌ ERRO GRAVE NO TESTE: {e}")
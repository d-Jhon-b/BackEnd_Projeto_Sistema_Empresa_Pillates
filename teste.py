# --- Imports e Configuração (Repetição para clareza) ---
from src.database.connPostGreNeon import CreateSessionPostGre
from sqlalchemy.orm import Session
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import logging
from sqlalchemy.exc import SQLAlchemyError

# Schemas e Models (Verifique os caminhos!)
from src.schemas.plano_schemas import PlanoCreate, TipoPlanoEnum, ModalidadePlanoEnum
from src.schemas.adesao_plano_schemas import SubscribePlano
from src.schemas.contrato_schemas import ContratoCreate, ContratoPlanoFKs, StatusContratoEnum
from src.schemas.solicitacao_schemas import SolicitacaoCreate, TipoDeSolicitacaoEnum

from src.model.PlanoModel import PlanosModel
from src.model.AdesaoPlanoModel import AdesaoPlanoModel
from src.model.ContratoModel import ContratoModel
from src.model.SolicitacoesModel import SolicitacoesModel 


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
create_session = CreateSessionPostGre()
session: Session = create_session.get_session()

FK_ID_ESTUDANTE = 1 
FK_ID_ESTUDIO = 1 # Usando o Estúdio 1, conforme o seu usuário


try:
    # --- 1. CRIAR PLANO PADRÃO (SIMULANDO CONTROLLER/SERVICE) ---
    print("\n--- 1. Criação de Plano Padrão ---")
    plano_repo = PlanosModel(session_db=session)
    plano_create_data = PlanoCreate(
        tipo_plano=TipoPlanoEnum.MENSAL,
        modalidade_plano=ModalidadePlanoEnum.DUAS_SEMANAS,
        descricao_plano="Plano mensal de teste para fluxo completo",
        valor_plano=Decimal('199.90'),
        qtde_aulas_totais=8
    )
    # Seu PlanoModel aceita o Schema, vamos manter assim por agora
    new_plano = plano_repo.insert_new_plano(plano_create_data) 
    
    if new_plano:
        FK_ID_PLANO_TESTE = new_plano.id_plano
        print(f"✅ SUCESSO! Plano Padrão criado. ID: {FK_ID_PLANO_TESTE}")
    else:
        raise Exception("FALHA: Não foi possível criar o Plano Padrão.")

    # --- 2. CRIAR ADESÃO AO PLANO ---
    print("\n--- 2. Criação de Adesão ao Plano ---")
    adesao_repo = AdesaoPlanoModel(session_db=session)

    DATA_ADESAO = datetime.now().replace(microsecond=0)
    DATA_VALIDADE = DATA_ADESAO + relativedelta(months=1)

    # Simulação do dicionário LIMPO que o Controller enviaria para o Model
    adesao_data_plana = {
        "fk_id_estudante": FK_ID_ESTUDANTE,
        "fk_id_plano": FK_ID_PLANO_TESTE,
        "fk_id_plano_personalizado": None,
        "data_adesao": DATA_ADESAO,
        "data_validade": DATA_VALIDADE
    }
    new_adesao = adesao_repo.subscribe_plan(adesao_data_plana)
    
    if new_adesao:
        FK_ID_ADESAO_TESTE = new_adesao.id_adesao_plano
        print(f"✅ SUCESSO! Adesão criada. ID: {FK_ID_ADESAO_TESTE}")
    else:
        raise Exception("FALHA: Não foi possível criar a Adesão ao Plano.")


    # --- 3. CRIAR CONTRATO ---
    print("\n--- 3. Criação de Contrato ---")
    contrato_repo = ContratoModel(session_db=session)

    # 1. Simulação do Payload Pydantic (entrada do Controller)
    payload_simulado = ContratoCreate(
        fk_id_estudante=FK_ID_ESTUDANTE,
        fk_id_adesao_plano=FK_ID_ADESAO_TESTE,
        plano_fks=ContratoPlanoFKs(fk_id_plano=FK_ID_PLANO_TESTE), 
        data_inicio=DATA_ADESAO,
        data_termino=DATA_VALIDADE,
        status_contrato=StatusContratoEnum.ATIVO
    )
    
    # 2. Simulação do DESANINHAMENTO no Controller para o Model
    contrato_data_bruta = payload_simulado.model_dump()
    plano_fks_data = contrato_data_bruta.pop('plano_fks')
    contrato_data_plana = {
        **contrato_data_bruta,
        'fk_id_plano': plano_fks_data.get('fk_id_plano'),
        'fk_id_plano_personalizado': plano_fks_data.get('fk_id_plano_personalizado')
    }
    
    new_contrato = contrato_repo.create_contract(contrato_data_plana)
    
    if new_contrato:
        FK_ID_CONTRATO_TESTE = new_contrato.id_contrato
        print(f"✅ SUCESSO! Contrato criado. ID: {FK_ID_CONTRATO_TESTE}")
    else:
        raise Exception("FALHA: Não foi possível criar o Contrato.")


    # --- 4. CRIAR SOLICITAÇÃO ---
    print("\n--- 4. Criação de Solicitação ---")
    solicitacoes_repo = SolicitacoesModel(session_db=session)

    # CORRIGIDO: Usando fk_id_estudante conforme o schema
    solicitacao_payload = SolicitacaoCreate(
        fk_id_estudante=FK_ID_ESTUDANTE, 
        fk_id_estudio=FK_ID_ESTUDIO,
        menssagem="Solicitação de agendamento após a criação do contrato.",
        tipo_de_solicitacao=TipoDeSolicitacaoEnum.AULA
    )
    
    # Seu SolicitacoesModel aceita o Schema, vamos manter assim por agora
    new_solicitacao = solicitacoes_repo.create_solicitacao(solicitacao_payload)
    
    if new_solicitacao:
        ID_SOLICITACAO_TESTE = new_solicitacao.id_solicitacao
        print(f"✅ SUCESSO! Solicitação criada. ID: {ID_SOLICITACAO_TESTE}")
    else:
        raise Exception("FALHA: Não foi possível criar a Solicitação.")
        
    session.commit() # Commit final se tudo deu certo
    
except SQLAlchemyError as err:
    print(f"\n❌ ERRO DE BANCO DE DADOS: {err}")
    session.rollback()

except Exception as e:
    print(f"\n❌ ERRO GERAL NO FLUXO DE TESTE: {e}")
    session.rollback() # Garante rollback em caso de falha


# --- 5. EXECUÇÃO DE OUTROS MÉTODOS DE SOLICITAÇÃO (OPCIONAL) ---
if 'ID_SOLICITACAO_TESTE' in locals():
    try:
        print("\n--- 5. Teste de Busca e Atualização de Solicitação ---")
        
        # BUSCAR POR ID
        solicitacao_buscada = solicitacoes_repo.select_solicitacao_by_id(ID_SOLICITACAO_TESTE)
        if solicitacao_buscada:
            print(f"✅ Busca por ID {ID_SOLICITACAO_TESTE} bem-sucedida. Status: {solicitacao_buscada.status_solicitacao}")

        # ATUALIZAR STATUS
        from src.schemas.solicitacao_schemas import SolicitacaoUpdate, StatusSolcitacaoEnum
        update_payload = SolicitacaoUpdate(status_solicitacao=StatusSolcitacaoEnum.ATENDIDA)
        
        # O método update_solicitacao espera o ID e o Schema, e o Model faz o dump
        updated_solicitacao = solicitacoes_repo.update_solicitacao(ID_SOLICITACAO_TESTE, update_payload)
        
        if updated_solicitacao and updated_solicitacao.status_solicitacao == StatusSolcitacaoEnum.ATENDIDA:
            print(f"✅ Atualização de status para 'ATENDIDA' bem-sucedida.")
        else:
             print("❌ Falha na atualização de status.")

        # BUSCAR TODAS FILTRADAS
        todas_solicitacoes = solicitacoes_repo.select_all_solicitacoes(id_estudio=FK_ID_ESTUDIO)
        print(f"✅ Busca por todas: {len(todas_solicitacoes)} solicitações encontradas para o Estúdio {FK_ID_ESTUDIO}.")
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES DE CRUD DE SOLICITAÇÃO: {e}")
        session.rollback()
        
    finally:
        session.commit() # Commit das alterações de atualização
        
        # --- LIMPEZA (OPCIONAL) ---
        print("\n--- 6. Teste de Exclusão de Solicitação ---")
        delete_result = solicitacoes_repo.delete_solicitacao(ID_SOLICITACAO_TESTE)
        if delete_result:
            print(f"✅ Exclusão da solicitação ID {ID_SOLICITACAO_TESTE} bem-sucedida.")
        else:
            print("❌ Falha na exclusão da solicitação.")
        session.commit()
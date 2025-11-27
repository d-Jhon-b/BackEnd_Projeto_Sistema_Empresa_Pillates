from src.model.planosModel.contratoConfig import Contrato
from src.model.UserModel import Usuario
from src.model.userModel.typeUser.aluno import Estudante
from src.model.solicitacoesModel.solicitacoesConfig import Solicitacoes
from src.services.pagamentosService import PagamentoService 
from src.schemas.contrato_schemas import ContratoCreate, ContratoResponse, StatusContratoEnum
from src.model.planosModel.adesaoPlanoConfig import AdesaoPlano
from src.model.planosModel.planosPersonalizadosConfig import PlanosPersonalizados
from src.model.planosModel.planoConfig import Planos


import logging
from typing import Dict, Any, Optional,List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select, delete, update
from sqlalchemy.exc import SQLAlchemyError


class ContratoModel():
    def __init__(self, session_db: Session):
        self.session = session_db

    def insert_new_contrato(self, data_to_insert: Dict[str, Any], current_user:Dict[str, Any]) -> Optional[Contrato]:
        print(current_user)
        fk_id_adesao_plano = data_to_insert.get('fk_id_adesao_plano')
        valor_negociado = data_to_insert.get('valor_final_negociado')
        
        try:
            adesao_db: Optional[AdesaoPlano] = self.session.query(AdesaoPlano).options(
                joinedload(AdesaoPlano.plano_padrao),
                joinedload(AdesaoPlano.plano_personalizado)
            ).filter(AdesaoPlano.id_adesao_plano == fk_id_adesao_plano).one_or_none()
            
            if not adesao_db: return None 

            valor_base = 0.0
            if adesao_db.plano_padrao:
                valor_base = adesao_db.plano_padrao.valor_plano
                qtde_aulas = adesao_db.plano_padrao.qtde_aulas_totais 
            elif adesao_db.plano_personalizado:
                valor_base = adesao_db.plano_personalizado.valor_plano 
                qtde_aulas = adesao_db.plano_personalizado.qtde_aulas_totais 
            
            data_inicio_contrato = adesao_db.data_adesao 
            data_termino_contrato = adesao_db.data_validade 
            
            valor_final_contrato = valor_negociado if valor_negociado is not None else valor_base

            new_contrato = Contrato(
                fk_id_estudante=adesao_db.fk_id_estudante, 
                fk_id_adesao_plano=fk_id_adesao_plano,
                fk_id_plano=adesao_db.fk_id_plano,
                fk_id_plano_personalizado=adesao_db.fk_id_plano_personalizado,
                data_inicio=data_inicio_contrato,
                data_termino=data_termino_contrato,
                valor_final=valor_final_contrato,
                aulas_restantes=qtde_aulas,
                status_contrato='ativo'
            )

            self.session.add(new_contrato)
            self.session.commit()
            self.session.refresh(new_contrato)
            
            # pagamento_service = PagamentoService(session_db=self.session)
            # parcelas = pagamento_service.gerar_pagamentos_contrato(new_contrato, current_user)
            # return new_contrato, parcelas
            pagamento_service = PagamentoService(session_db=self.session)
            parcelas = pagamento_service.gerar_pagamentos_contrato(new_contrato, current_user)
                        
            # Retorna o ID e as parcelas
            return new_contrato.id_contrato, parcelas
            
        except SQLAlchemyError as err:
            logging.error(f"Erro de Banco de Dados ao criar Contrato: {err}")
            self.session.rollback()
            return None
        except Exception as err:
            logging.error(f"Erro Inserir novo contrato: {err}")
            self.session.rollback()
            return None
        

    def select_contrato_by_id(self, contrato_id: int) -> Optional[Contrato]:
        """Busca um contrato pelo ID, carregando adesão e planos associados."""
        try:
            stmt = (
                select(Contrato)
                .where(Contrato.id_contrato == contrato_id)
                .options(joinedload(Contrato.adesao_plano))
                .options(joinedload(Contrato.plano))
                .options(joinedload(Contrato.plano_personalizado))
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar Contrato {contrato_id}: {err}")
            return None

    def select_active_contract_by_estudante(self, fk_id_estudante: int) -> Optional[Contrato]:
        """Busca o contrato ativo (ou suspenso) de um estudante."""
        try:
            stmt = select(Contrato).where(
                Contrato.fk_id_estudante == fk_id_estudante,
                Contrato.status_contrato.in_(['ativo', 'suspenso'])
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar contrato ativo do estudante {fk_id_estudante}: {err}")
            return None
            
    # def update_contrato_data(self, contrato_id: int, data_to_update: Dict[str, Any]) -> Optional[Contrato]:
    def update_contrato(self, contrato_id: int, data_to_update: Dict[str, Any]) -> Optional[Contrato]:
        update_dict = {k: v for k, v in data_to_update.items() if v is not None}
        if not update_dict:
            return self.session.get(Contrato, contrato_id)

        try:
            update_stmt = (
                update(Contrato)
                .where(Contrato.id_contrato == contrato_id)
                .values(**update_dict)
            )
            
            result = self.session.execute(update_stmt)
            if result.rowcount == 0:
                self.session.rollback()
                return None
                
            self.session.commit()
            return self.session.get(Contrato, contrato_id)
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao atualizar Contrato {contrato_id}: {err}")
            self.session.rollback()
            return None 


    def select_all_contracts_by_estudante(self, fk_id_estudante: int) -> List[Contrato]:
        contratos = self.session.query(Contrato).options(
            joinedload(Contrato.plano), 
            joinedload(Contrato.plano_personalizado),
            joinedload(Contrato.adesao_plano)
        ).filter(
            Contrato.fk_id_estudante == fk_id_estudante
        ).order_by(
            Contrato.data_inicio.desc() 
        ).all()
        return contratos
    

    def update_contract_status(self, id_contrato:int, update_type:str):
        try:
            stmt_update_status = (
                update(Contrato)
                .where(Contrato.id_contrato == id_contrato)
                .values(status_contrato=update_type) 
            )
            
            result = self.session.execute(stmt_update_status)
            
            if result.rowcount == 0:
                self.session.rollback()
                return None
            self.session.commit()

            return self.session.get(Contrato, id_contrato)
        except SQLAlchemyError as err:
            logging.error(f'Erro ao processar update de status do contrato.\nerro:{err}')
            return None
        except Exception as err:
            logging.error(f'Erro ao processar update de status do contrato.\nerro:{err}')
            return None
        

    #----------------------------Métodos para uso do Serviço de Adesão+Contrato
    def select_contrato_by_adesao(self, fk_id_adesao_plano: int) -> Optional[Contrato]:
        try:
            stmt = (
                select(Contrato)
                .where(Contrato.fk_id_adesao_plano == fk_id_adesao_plano)
            )
            return self.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as err:
            logging.error(f"Erro de DB ao buscar Contrato por Adesão ID {fk_id_adesao_plano}: {err}")
            return None

    def delete_contrato_by_id(self, contrato_id: int) -> bool:
        try:
            stmt = delete(Contrato).where(Contrato.id_contrato == contrato_id)
            res_delete = self.session.execute(stmt)
            return res_delete.rowcount > 0
        except Exception as err:
            logging.error(f"Erro ao deletar Contrato {contrato_id}: {err}")
            raise




# import logging
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import Dict, Any
# from dateutil.relativedelta import relativedelta
# # Suas importações
# from src.database.connPostGreNeon import CreateSessionPostGre 
# from src.schemas.contrato_schemas import ContratoResponse, StatusContratoEnum 
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# create_session = CreateSessionPostGre()
# session: Session = create_session.get_session()

# contrato_repo = ContratoModel(session_db=session)

# DATA_ADESAO = datetime.now().replace(microsecond=0)
# # A validade para um plano mensal (tipo_plano=MENSAL) é de 1 mês
# DATA_VALIDADE = DATA_ADESAO + relativedelta(months=1)
# FK_ID_ESTUDANTE=1
# FK_ID_ADESAO_TESTE = 1
# FK_ID_PLANO_TESTE =1
# DATA_INICIO_CONTRATO = DATA_ADESAO
# DATA_TERMINO_CONTRATO = DATA_VALIDADE # O término do contrato coincide com a validade do plano

# if FK_ID_ADESAO_TESTE and FK_ID_PLANO_TESTE:
#     # 1. Simulação do Schema de Entrada (Payload do Controller)
#     payload_simulado = ContratoCreate(
#         fk_id_estudante=FK_ID_ESTUDANTE,
#         fk_id_adesao_plano=FK_ID_ADESAO_TESTE,
#         plano_fks=ContratoPlanoFKs(fk_id_plano=FK_ID_PLANO_TESTE), # O campo aninhado!
#         data_inicio=DATA_INICIO_CONTRATO,
#         data_termino=DATA_TERMINO_CONTRATO,
#         status_contrato=StatusContratoEnum.ATIVO
#     )
    
#     # 2. Simulação do DESANINHAMENTO no Controller
#     contrato_data_bruta = payload_simulado.model_dump()
#     plano_fks_data = contrato_data_bruta.pop('plano_fks')
    
#     # 3. Montar o dicionário LIMPO para o Model
#     contrato_data_plana = {
#         **contrato_data_bruta,
#         'fk_id_plano': plano_fks_data.get('fk_id_plano'),
#         'fk_id_plano_personalizado': plano_fks_data.get('fk_id_plano_personalizado')
#     }
    
#     try:
#         new_contrato = contrato_repo.create_contract(contrato_data_plana)
        
#         if new_contrato:
#             FK_ID_CONTRATO_TESTE = new_contrato.id_contrato
#             print(f" SUCESSO! Contrato criado. ID: {FK_ID_CONTRATO_TESTE}")
#             print(f"   Status: {new_contrato.status_contrato}, Plano FK: {new_contrato.fk_id_plano}")
#         else:
#             FK_ID_CONTRATO_TESTE = None
#             print(" FALHA ao criar Contrato.")

#     except Exception as e:
#         session.rollback()
#         print(f" ERRO no Teste Contrato: {e}")
#         FK_ID_CONTRATO_TESTE = None
# else:
#     print("Pulando Contrato: Adesão e/ou Plano não foram criados.")
#     FK_ID_CONTRATO_TESTE = None
from src.model.planosModel.planoModel import PlanoModel
from src.schemas.plano_schemas import PlanoDetalhe

def criar_plano_controller(usuario_id, plano_dados, session):
    plano_dados["fk_usuario"] = usuario_id
    novo_plano = PlanoModel.adicionar_plano(session, plano_dados)
    return PlanoDetalhe.from_orm(novo_plano)


def listar_planos_controller(usuario_id, session):
    planos = PlanoModel.buscar_planos_por_usuario(session, usuario_id)
    return [PlanoDetalhe.from_orm(p) for p in planos]


def meus_planos_controller(usuario_id, session):
    planos = PlanoModel.buscar_planos_por_usuario(session, usuario_id)
    return [PlanoDetalhe.from_orm(plano) for plano in planos]

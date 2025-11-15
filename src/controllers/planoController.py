# from src.model.planosModel.planoModel import PlanoModel
# from src.schemas.plano_schemas import PlanoDetalhe  # Exemplo: esquema global para respostas

# def criar_plano_controller(usuario_id, plano_dados, session):
#     novo_plano = PlanoModel.adicionar_plano(session, plano_dados)
#     return novo_plano

# def listar_planos_controller(usuario_id, session):
#     planos = PlanoModel.buscar_planos_por_usuario(session, usuario_id)
#     return planos

# def meus_planos_controller(usuario_id: int):
#     # Consulta todos os planos do usuário logado
#     planos = PlanoModel.buscar_planos_por_usuario(usuario_id)
#     # Transforma para resposta (ex: Pydantic para API REST)
#     return [PlanoDetalhe.from_orm(plano) for plano in planos]
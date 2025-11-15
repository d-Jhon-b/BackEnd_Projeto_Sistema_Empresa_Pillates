from src.database.connPostGreNeon import CreateSessionPostGre
from src.model.planosModel.planosConfig import Planos
from src.model.UserModel import Usuario


class PlanoModel:
    @staticmethod
    def buscar_planos_por_usuario(usuario_id: int):
        """
        Retorna todos os planos vinculados a um determinado usuário.
        """
        session = CreateSessionPostGre()
        try:
            planos = session.query(Planos).filter(Planos.usuario_id == usuario_id).all()
            return planos
        finally:
            session.close()

    @staticmethod
    def adicionar_plano(plano_dados: dict):
        """
        Adiciona um novo plano ao banco de dados.
        """
        session = CreateSessionPostGre()
        try:
            novo_plano = Planos(**plano_dados)  # usa unpacking do dicionário
            session.add(novo_plano)
            session.commit()
            session.refresh(novo_plano)
            return novo_plano
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


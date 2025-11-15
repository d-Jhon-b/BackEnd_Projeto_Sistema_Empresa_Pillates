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
        create_session = CreateSessionPostGre()
        session = create_session.get_session()

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

class PlanoModel:
    @staticmethod
    def get_all_planos(db):
        return db.query(Planos).all()

    @staticmethod
    def create_plano(db, plano_create):
        novo_plano = Planos(**plano_create.dict())
        db.add(novo_plano)
        db.commit()
        db.refresh(novo_plano)
        return novo_plano


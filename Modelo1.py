from datetime import datetime

# Bibliotecas para conexão com banco SQL e MongoDB
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient

# Configurações de conexão (substituir pelos valores reais)
SQLALCHEMY_DATABASE_URL = "postgresql://usuario:senha@localhost:5432/seubanco"
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"

Base = declarative_base()

# ----- SQL Alchemy Models ------

class UsuarioSQL(Base):
    __tablename__ = 'usuario'
    idUser = Column(Integer, primary_key=True, autoincrement=True)
    nomeUser = Column(String(255), nullable=False)
    fotoUser = Column(String(36))
    tipoDocUser = Column(String(20))
    numDocUser = Column(String(14))
    nascUser = Column(Date)
    tipoUsuario = Column(String(50))

class PlanoSQL(Base):
    __tablename__ = 'plano'
    idPlano = Column(Integer, primary_key=True, autoincrement=True)
    descricaoPlano = Column(String(255))
    tipoPlano = Column(String(50))
    duracaoMeses = Column(Integer)
    numAulasIncluidas = Column(Integer)
    valorPlano = Column(Float)
    usuarioId = Column(Integer, ForeignKey("usuario.idUser"))

class AulaSQL(Base):
    __tablename__ = 'aula'
    idAula = Column(Integer, primary_key=True, autoincrement=True)
    dataAula = Column(DateTime)
    descAula = Column(String(255))
    estudioId = Column(Integer)
    professorId = Column(Integer)

class PagamentoSQL(Base):
    __tablename__ = 'pagamento'
    idPagamento = Column(Integer, primary_key=True, autoincrement=True)
    contratoId = Column(Integer)
    estudanteId = Column(Integer)
    valorPagamento = Column(Float)
    dataPagamento = Column(Date)
    metodoPagamento = Column(String(50))
    statusPagamento = Column(String(50))

# ----- Conexões -----

# Conexão SQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Conexão MongoDB
mongo_client = MongoClient(MONGODB_CONNECTION_STRING)
mongo_db = mongo_client['pilates_db']

# ----- Classes Python com métodos para salvar no SQL e Mongo -----

class Usuario:
    def __init__(self, idUser, nomeUser, fotoUser, tipoDocUser, numDocUser, nascUser, tipoUsuario):
        self.idUser = idUser
        self.nomeUser = nomeUser
        self.fotoUser = fotoUser
        self.tipoDocUser = tipoDocUser
        self.numDocUser = numDocUser
        self.nascUser = nascUser
        self.tipoUsuario = tipoUsuario

    def save_sql(self):
        db = SessionLocal()
        user = UsuarioSQL(
            idUser = self.idUser,
            nomeUser = self.nomeUser,
            fotoUser = self.fotoUser,
            tipoDocUser = self.tipoDocUser,
            numDocUser = self.numDocUser,
            nascUser = self.nascUser,
            tipoUsuario = self.tipoUsuario
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user.idUser

    def save_mongo(self):
        doc = {
            "nomeUser": self.nomeUser,
            "fotoUser": self.fotoUser,
            "tipoDocUser": self.tipoDocUser,
            "numDocUser": self.numDocUser,
            "nascUser": self.nascUser,
            "tipoUsuario": self.tipoUsuario,
        }
        result = mongo_db.usuarios.insert_one(doc)
        return str(result.inserted_id)

class Plano:
    def __init__(self, idPlano, descricaoPlano, tipoPlano, duracaoMeses, numAulasIncluidas, valorPlano, usuarioId):
        self.idPlano = idPlano
        self.descricaoPlano = descricaoPlano
        self.tipoPlano = tipoPlano
        self.duracaoMeses = duracaoMeses
        self.numAulasIncluidas = numAulasIncluidas
        self.valorPlano = valorPlano
        self.usuarioId = usuarioId

    def save_sql(self):
        db = SessionLocal()
        plano = PlanoSQL(
            idPlano = self.idPlano,
            descricaoPlano = self.descricaoPlano,
            tipoPlano = self.tipoPlano,
            duracaoMeses = self.duracaoMeses,
            numAulasIncluidas = self.numAulasIncluidas,
            valorPlano = self.valorPlano,
            usuarioId = self.usuarioId
        )
        db.add(plano)
        db.commit()
        db.refresh(plano)
        db.close()
        return plano.idPlano

    def save_mongo(self):
        doc = {
            "descricaoPlano": self.descricaoPlano,
            "tipoPlano": self.tipoPlano,
            "duracaoMeses": self.duracaoMeses,
            "numAulasIncluidas": self.numAulasIncluidas,
            "valorPlano": self.valorPlano,
            "usuarioId": self.usuarioId
        }
        result = mongo_db.planos.insert_one(doc)
        return str(result.inserted_id)

class Aula:
    def __init__(self, idAula, dataAula, descAula, estudioId, professorId):
        self.idAula = idAula
        self.dataAula = dataAula
        self.descAula = descAula
        self.estudioId = estudioId
        self.professorId = professorId

    def save_sql(self):
        db = SessionLocal()
        aula = AulaSQL(
            idAula = self.idAula,
            dataAula = self.dataAula,
            descAula = self.descAula,
            estudioId = self.estudioId,
            professorId = self.professorId
        )
        db.add(aula)
        db.commit()
        db.refresh(aula)
        db.close()
        return aula.idAula

    def save_mongo(self):
        doc = {
            "dataAula": self.dataAula,
            "descAula": self.descAula,
            "estudioId": self.estudioId,
            "professorId": self.professorId
        }
        result = mongo_db.aulas.insert_one(doc)
        return str(result.inserted_id)

class Pagamento:
    def __init__(self, idPagamento, contratoId, estudanteId, valorPagamento, dataPagamento, metodoPagamento, statusPagamento):
        self.idPagamento = idPagamento
        self.contratoId = contratoId
        self.estudanteId = estudanteId
        self.valorPagamento = valorPagamento
        self.dataPagamento = dataPagamento
        self.metodoPagamento = metodoPagamento
        self.statusPagamento = statusPagamento

    def save_sql(self):
        db = SessionLocal()
        pagamento = PagamentoSQL(
            idPagamento = self.idPagamento,
            contratoId = self.contratoId,
            estudanteId = self.estudanteId,
            valorPagamento = self.valorPagamento,
            dataPagamento = self.dataPagamento,
            metodoPagamento = self.metodoPagamento,
            statusPagamento = self.statusPagamento
        )
        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)
        db.close()
        return pagamento.idPagamento

    def save_mongo(self):
        doc = {
            "contratoId": self.contratoId,
            "estudanteId": self.estudanteId,
            "valorPagamento": self.valorPagamento,
            "dataPagamento": self.dataPagamento,
            "metodoPagamento": self.metodoPagamento,
            "statusPagamento": self.statusPagamento
        }
        result = mongo_db.pagamentos.insert_one(doc)
        return str(result.inserted_id)

# Exemplo de uso:
if __name__ == "__main__":
    usuario = Usuario(None, "João Silva", "foto1.jpg", "CPF", "12345678900", datetime(1990, 5, 12), "Aluno")
    usuario_id_sql = usuario.save_sql()
    usuario_id_mongo = usuario.save_mongo()
    print("Usuario inserido SQL id:", usuario_id_sql)
    print("Usuario inserido Mongo id:", usuario_id_mongo)

    plano = Plano(None, "Plano Mensal Pilates", "Mensal", 1, 8, 150.00, usuario_id_sql)
    plano_id_sql = plano.save_sql()
    plano_id_mongo = plano.save_mongo()
    print("Plano inserido SQL id:", plano_id_sql)
    print("Plano inserido Mongo id:", plano_id_mongo)

    aula = Aula(None, datetime(2025, 9, 28, 18, 30), "Pilates Intermediário", 1, 10)
    aula_id_sql = aula.save_sql()
    aula_id_mongo = aula.save_mongo()
    print("Aula inserida SQL id:", aula_id_sql)
    print("Aula inserida Mongo id:", aula_id_mongo)

    pagamento = Pagamento(None, 1001, usuario_id_sql, 150.00, datetime(2025, 9, 1), "PIX", "Pago")
    pagamento_id_sql = pagamento.save_sql()
    pagamento_id_mongo = pagamento.save_mongo()
    print("Pagamento inserido SQL id:", pagamento_id_sql)
    print("Pagamento inserido Mongo id:", pagamento_id_mongo)

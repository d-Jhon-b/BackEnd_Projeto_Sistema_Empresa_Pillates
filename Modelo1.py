from datetime import datetime

# Classes modelo orientadas a objetos

class Usuario:
    def __init__(self, idUser, nomeUser, fotoUser, tipoDocUser, numDocUser, nascUser, tipoUsuario):
        self.idUser = idUser
        self.nomeUser = nomeUser
        self.fotoUser = fotoUser
        self.tipoDocUser = tipoDocUser
        self.numDocUser = numDocUser
        self.nascUser = nascUser
        self.tipoUsuario = tipoUsuario
    
    def insert_sql(self):
        return (
            f"INSERT INTO Usuario (idUser, nomeUser, fotoUser, tipoDocUser, numDocUser, nascUser, tipoUsuario) "
            f"VALUES ({self.idUser or 'DEFAULT'}, '{self.nomeUser}', '{self.fotoUser}', '{self.tipoDocUser}', "
            f"'{self.numDocUser}', '{self.nascUser.strftime('%Y-%m-%d')}', '{self.tipoUsuario}');"
        )
    
    def insert_mongo(self):
        return {
            "_id": self.idUser,
            "nomeUser": self.nomeUser,
            "fotoUser": self.fotoUser,
            "tipoDocUser": self.tipoDocUser,
            "numDocUser": self.numDocUser,
            "nascUser": self.nascUser.isoformat(),
            "tipoUsuario": self.tipoUsuario,
        }

class Plano:
    def __init__(self, idPlano, descricaoPlano, tipoPlano, duracaoMeses, numAulasIncluidas, valorPlano, usuarioId):
        self.idPlano = idPlano
        self.descricaoPlano = descricaoPlano
        self.tipoPlano = tipoPlano
        self.duracaoMeses = duracaoMeses
        self.numAulasIncluidas = numAulasIncluidas
        self.valorPlano = valorPlano
        self.usuarioId = usuarioId
    
    def insert_sql(self):
        return (
            f"INSERT INTO Plano (idPlano, descricaoPlano, tipoPlano, duracaoMeses, numAulasIncluidas, valorPlano, usuarioId) "
            f"VALUES ({self.idPlano or 'DEFAULT'}, '{self.descricaoPlano}', '{self.tipoPlano}', {self.duracaoMeses}, "
            f"{self.numAulasIncluidas}, {self.valorPlano:.2f}, {self.usuarioId});"
        )
    
    def insert_mongo(self):
        return {
            "_id": self.idPlano,
            "descricaoPlano": self.descricaoPlano,
            "tipoPlano": self.tipoPlano,
            "duracaoMeses": self.duracaoMeses,
            "numAulasIncluidas": self.numAulasIncluidas,
            "valorPlano": self.valorPlano,
            "usuarioId": self.usuarioId,
        }

class Aula:
    def __init__(self, idAula, dataAula, descAula, estudioId, professorId):
        self.idAula = idAula
        self.dataAula = dataAula
        self.descAula = descAula
        self.estudioId = estudioId
        self.professorId = professorId
    
    def insert_sql(self):
        return (
            f"INSERT INTO Aula (idAula, dataAula, descAula, estudioId, professorId) VALUES "
            f"({self.idAula or 'DEFAULT'}, '{self.dataAula.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"'{self.descAula}', {self.estudioId}, {self.professorId});"
        )
    
    def insert_mongo(self):
        return {
            "_id": self.idAula,
            "dataAula": self.dataAula.isoformat(),
            "descAula": self.descAula,
            "estudioId": self.estudioId,
            "professorId": self.professorId,
        }

class Pagamento:
    def __init__(self, idPagamento, contratoId, estudanteId, valorPagamento, dataPagamento, metodoPagamento, statusPagamento):
        self.idPagamento = idPagamento
        self.contratoId = contratoId
        self.estudanteId = estudanteId
        self.valorPagamento = valorPagamento
        self.dataPagamento = dataPagamento
        self.metodoPagamento = metodoPagamento
        self.statusPagamento = statusPagamento
    
    def insert_sql(self):
        return (
            f"INSERT INTO Pagamento (idPagamento, contratoId, estudanteId, valorPagamento, dataPagamento, metodoPagamento, statusPagamento) VALUES "
            f"({self.idPagamento or 'DEFAULT'}, {self.contratoId}, {self.estudanteId}, {self.valorPagamento:.2f}, "
            f"'{self.dataPagamento.strftime('%Y-%m-%d')}', '{self.metodoPagamento}', '{self.statusPagamento}');"
        )
    
    def insert_mongo(self):
        return {
            "_id": self.idPagamento,
            "contratoId": self.contratoId,
            "estudanteId": self.estudanteId,
            "valorPagamento": self.valorPagamento,
            "dataPagamento": self.dataPagamento.isoformat(),
            "metodoPagamento": self.metodoPagamento,
            "statusPagamento": self.statusPagamento,
        }

# Exemplo de uso com dados fictícios para inserção:

usuario = Usuario(
    idUser=None,
    nomeUser="João Silva",
    fotoUser="foto1.jpg",
    tipoDocUser="CPF",
    numDocUser="12345678900",
    nascUser=datetime(1990, 5, 12),
    tipoUsuario="Aluno"
)

plano = Plano(
    idPlano=None,
    descricaoPlano="Plano Mensal Pilates",
    tipoPlano="Mensal",
    duracaoMeses=1,
    numAulasIncluidas=8,
    valorPlano=150.00,
    usuarioId=1
)

aula = Aula(
    idAula=None,
    dataAula=datetime(2025, 9, 28, 18, 30),
    descAula="Pilates Intermediário",
    estudioId=1,
    professorId=10
)

pagamento = Pagamento(
    idPagamento=None,
    contratoId=1001,
    estudanteId=1,
    valorPagamento=150.00,
    dataPagamento=datetime(2025, 9, 1),
    metodoPagamento="PIX",
    statusPagamento="Pago"
)

# Impressão dos comandos SQL:
print(usuario.insert_sql())
print(plano.insert_sql())
print(aula.insert_sql())
print(pagamento.insert_sql())

# Impressão dos documentos MongoDB simulados:
print(usuario.insert_mongo())
print(plano.insert_mongo())
print(aula.insert_mongo())
print(pagamento.insert_mongo())

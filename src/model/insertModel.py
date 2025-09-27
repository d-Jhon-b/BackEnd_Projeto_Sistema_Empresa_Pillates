from src.database.connPostGre import PostGreModel


class InserTypeOperation():
    def __init__(self):
        postGre = PostGreModel()
        conPostGRe = postGre.connect_db()
        discPostGRe = postGre.diconnect_db()

    def InsertUser():
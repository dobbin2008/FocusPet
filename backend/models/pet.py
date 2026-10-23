from urllib.parse import quote

from backend.extensions import db
from backend.models.base import CrudModel


class Pet(CrudModel, db.Model):
    __tablename__ = "pets"
    XP_POR_NIVEL = 100
    NIVEL_MAXIMO = 10
    CATALOGO = {
        "grup0": {
            "nomes": ("Weedle", "Kakuna", "Beedrill"),
            "imagens": (
                "weedle base grup0.png",
                "kakuna evo1 grup0.png",
                "beedrill evo2 grup0.png",
            ),
            "niveis_evolucao": (4, 9),
            "inicial": True,
        },
        "grup1": {
            "nomes": ("Elekid", "Electabuzz", "Electivire"),
            "imagens": (
                "elekid base grup1.png",
                "electabuzz evo1 grup1.png",
                "electivire evo2 grup1.png",
            ),
            "niveis_evolucao": (4, 9),
            "inicial": True,
        },
        "grup2": {
            "nomes": ("Charmander", "Charmeleon", "Charizard"),
            "imagens": (
                "charmander base grup2.png",
                "charmeleon evo1 grup2.png",
                "charizard evo2 grup2.png",
            ),
            "niveis_evolucao": (4, 9),
        },
        "grup3": {
            "nomes": ("Mewtwo",),
            "imagens": ("mewtwo base grup3.png",),
            "niveis_evolucao": (),
        },
        "grup4": {
            "nomes": ("Suicune",),
            "imagens": ("suicune base grup4.png",),
            "niveis_evolucao": (),
        },
        "grup5": {
            "nomes": ("Slakoth", "Vigoroth", "Slaking"),
            "imagens": (
                "slakoth base grup5.png",
                "vigoroth evo1 grup6.png",
                "slaking evo2 grup6.png",
            ),
            "niveis_evolucao": (4, 9),
        },
        "grup7": {
            "nomes": ("Squirtle", "Wartortle", "Blastoise"),
            "imagens": (
                "squirtle base grup7.png",
                "wartortle evo1 grup7.png",
                "blastoise evo2 grup7.png",
            ),
            "niveis_evolucao": (4, 9),
        },
        "grup8": {
            "nomes": ("Aron", "Lairon", "Aggron"),
            "imagens": (
                "aron base grup8.png",
                "lairon evo1 grup8.png",
                "aggron evo2 grup8.png",
            ),
            "niveis_evolucao": (4, 9),
        },
        "grup9": {
            "nomes": ("Wailmer", "Wailord"),
            "imagens": ("wailmer base grup9.png", "wailord evo1 grup9.png"),
            "niveis_evolucao": (7,),
        },
        "grup10": {
            "nomes": ("Genesect",),
            "imagens": ("genesect base grup10.png",),
            "niveis_evolucao": (),
        },
        "grup11": {
            "nomes": ("Grubbin", "Charjabug", "Vikavolt"),
            "imagens": (
                "grubbin base grup11.png",
                "charjabug evo1 grup11.png",
                "vikavolt evo2 grup11.png",
            ),
            "niveis_evolucao": (4, 9),
        },
        "grup12": {
            "nomes": ("Hoopa", "Hoopa Unbound"),
            "imagens": ("hoopa base grup12.png", "hoopa unbound evo1 grup12.png"),
            "niveis_evolucao": (7,),
        },
        "grup13": {
            "nomes": ("Nymble", "Lokix"),
            "imagens": ("nymble base grup13.png", "lokix evo1 grup13.png"),
            "niveis_evolucao": (7,),
        },
        "grup14": {
            "nomes": ("Dreepy", "Drakloak", "Dragapult"),
            "imagens": (
                "dreepy base grup14.png",
                "drakloak evo1 grup14.png",
                "dragapult evo2 grup14.png",
            ),
            "niveis_evolucao": (4, 9),
        },
    }

    nome = db.Column(db.String(120), nullable=False)
    nivel = db.Column(db.Integer, default=1)
    linha_evolutiva = db.Column(db.String(20), nullable=False, default="grup0", server_default="grup0")
    descricao = db.Column(db.String(255))
    imagem = db.Column(db.String(255))
    imagem_nivel_1 = db.Column(db.String(255))
    imagem_nivel_2 = db.Column(db.String(255))
    imagem_nivel_3 = db.Column(db.String(255))
    xp_atual = db.Column(db.Integer, default=0)
    eh_padrao = db.Column(db.Boolean, default=False)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"))

    @staticmethod
    def calcular_nivel(xp_total):
        return min(Pet.NIVEL_MAXIMO, max(1, int(xp_total or 0) // Pet.XP_POR_NIVEL + 1))

    @property
    def evolucao(self):
        nivel = self.nivel or self.calcular_nivel(self.xp_atual)
        catalogo = self.CATALOGO.get(self.linha_evolutiva)
        if catalogo is None:
            return 0
        return sum(nivel >= marco for marco in catalogo["niveis_evolucao"])

    @property
    def imagem_url(self):
        catalogo = self.CATALOGO.get(self.linha_evolutiva, self.CATALOGO["grup0"])
        imagens = catalogo["imagens"]
        return f"/static/img/{quote(imagens[self.evolucao], safe='')}"

    @property
    def nome_atual(self):
        catalogo = self.CATALOGO.get(self.linha_evolutiva, self.CATALOGO["grup0"])
        nomes = catalogo["nomes"]
        return nomes[self.evolucao]

    @property
    def xp_progresso_nivel(self):
        if self.nivel >= self.NIVEL_MAXIMO:
            return self.XP_POR_NIVEL
        xp_inicio_nivel = (self.nivel - 1) * self.XP_POR_NIVEL
        return max(0, (self.xp_atual or 0) - xp_inicio_nivel)

    @property
    def xp_para_proximo_nivel(self):
        if self.nivel >= self.NIVEL_MAXIMO:
            return 0
        return max(0, self.XP_POR_NIVEL - self.xp_progresso_nivel)

    def sincronizar_nivel(self):
        self.nivel = self.calcular_nivel(self.xp_atual)
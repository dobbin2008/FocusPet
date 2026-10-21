from urllib.parse import quote

from backend.extensions import db
from backend.models.base import CrudModel


class Pet(CrudModel, db.Model):
    __tablename__ = "pets"
    XP_POR_NIVEL = 100
    NIVEL_MAXIMO = 10
    IMAGENS_EVOLUCAO = {
        "grup0": (
            "weedle base grup0.png",
            "kakuna evo1 grup0.png",
            "beedrill evo2 grup0.png",
        ),
        "grup1": (
            "elekid base grup1.png",
            "electabuzz evo1 grup1.png",
            "electivire evo2 grup1.png",
        ),
    }
    NOMES_EVOLUCAO = {
        "grup0": ("Weedle", "Kakuna", "Beedrill"),
        "grup1": ("Elekid", "Electabuzz", "Electivire"),
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
    tribo_id = db.Column(db.Integer, db.ForeignKey("tribos.id", ondelete="SET NULL"))

    @staticmethod
    def calcular_nivel(xp_total):
        return min(Pet.NIVEL_MAXIMO, max(1, int(xp_total or 0) // Pet.XP_POR_NIVEL + 1))

    @property
    def evolucao(self):
        nivel = self.nivel or self.calcular_nivel(self.xp_atual)
        if nivel >= 9:
            return 2
        if nivel >= 4:
            return 1
        return 0

    @property
    def imagem_url(self):
        imagens = self.IMAGENS_EVOLUCAO.get(self.linha_evolutiva, self.IMAGENS_EVOLUCAO["grup0"])
        return f"/static/img/{quote(imagens[self.evolucao], safe='')}"

    @property
    def nome_atual(self):
        nomes = self.NOMES_EVOLUCAO.get(self.linha_evolutiva, self.NOMES_EVOLUCAO["grup0"])
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
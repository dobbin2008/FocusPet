from .database import db


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    nivel = db.Column(db.Integer, default=1)
    descricao = db.Column(db.String(255), nullable=True)
    imagem = db.Column(db.String(255), nullable=True)
    imagem_nivel_1 = db.Column(db.String(255), nullable=True)
    imagem_nivel_2 = db.Column(db.String(255), nullable=True)
    imagem_nivel_3 = db.Column(db.String(255), nullable=True)
    xp_atual = db.Column(db.Integer, default=0)
    eh_padrao = db.Column(db.Boolean, default=False)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=True)
    tribo_id = db.Column(db.Integer, db.ForeignKey("tribos.id"), nullable=True)

    dono = db.relationship(
        "Estudante",
        back_populates="pets",
        foreign_keys=[estudante_id],
        lazy="select",
    )
    tribo = db.relationship("Tribo", back_populates="pets_de_tribo")

    MAX_NIVEL = 10

    def ganhar_xp(self, quantidade: int) -> None:
        self.xp_atual = max(0, self.xp_atual + quantidade)
        self.evoluir()

    def evoluir(self) -> None:
        while self.nivel < self.MAX_NIVEL and self.xp_atual >= self.xp_para_proximo_nivel():
            self.xp_atual -= self.xp_para_proximo_nivel()
            self.nivel += 1
            self.atualizar_imagem_por_nivel()

    def xp_para_proximo_nivel(self) -> int:
        return self.nivel * 100

    def atualizar_imagem_por_nivel(self) -> None:
        if self.nivel < 4:
            self.imagem = self.imagem_nivel_1 or self.imagem
        elif self.nivel < 9:
            self.imagem = self.imagem_nivel_2 or self.imagem
        else:
            self.imagem = self.imagem_nivel_3 or self.imagem

    def definir_imagens(self, nivel_1: str, nivel_2: str, nivel_3: str) -> None:
        self.imagem_nivel_1 = nivel_1
        self.imagem_nivel_2 = nivel_2
        self.imagem_nivel_3 = nivel_3
        if self.nivel < 4:
            self.imagem = nivel_1
        elif self.nivel < 9:
            self.imagem = nivel_2
        else:
            self.imagem = nivel_3

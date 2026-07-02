from .database import db


class Tribo(db.Model):
    __tablename__ = "tribos"

    id = db.Column(db.Integer, primary_key=True)
    materia = db.Column(db.String(120), nullable=False)

    membros = db.relationship("Estudante", backref="tribo", lazy="dynamic")
    pets_de_tribo = db.relationship("Pet", back_populates="tribo", cascade="all, delete-orphan")

    def adicionar_membro(self, estudante) -> None:
        if estudante not in self.membros:
            self.membros.append(estudante)

    def remover_membro(self, estudante) -> None:
        if estudante in self.membros:
            self.membros.remove(estudante)

    def exibir_ranking(self):
        return sorted(self.membros, key=lambda estudante: estudante.xp_total, reverse=True)

    def desbloquear_pet_exclusivo(self, estudante) -> None:
        if estudante in self.membros:
            estudante.adicionar_xp(10)

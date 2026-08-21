from .database import db


class Tribo(db.Model):
    __tablename__ = "tribos"

    id = db.Column(db.Integer, primary_key=True)
    materia = db.Column(db.String(120), nullable=False)

    membros = db.relationship("Estudante", backref="tribo", lazy="dynamic")
    pets_de_tribo = db.relationship("Pet", back_populates="tribo", cascade="all, delete-orphan")

    @classmethod
    def criar(cls, materia: str) -> "Tribo":
        if not materia or not materia.strip():
            raise ValueError("Matéria é obrigatória")

        tribo = cls(materia=materia.strip())
        db.session.add(tribo)
        db.session.commit()
        return tribo

    @classmethod
    def listar_todos(cls):
        return cls.query.all()

    @classmethod
    def deletar_por_id(cls, tribo_id: int) -> bool:
        tribo = cls.query.get(tribo_id)
        if tribo:
            db.session.delete(tribo)
            db.session.commit()
            return True
        return False

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

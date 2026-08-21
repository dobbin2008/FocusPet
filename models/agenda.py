from datetime import datetime
from .database import db


class Agenda(db.Model):
    __tablename__ = "agendas"

    id = db.Column(db.Integer, primary_key=True)
    data_atual = db.Column(db.DateTime, default=datetime.utcnow)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

    estudante = db.relationship("Estudante", back_populates="agenda")
    estudos = db.relationship("Estudo", back_populates="agenda", cascade="all, delete-orphan")

    def adicionar_horario(self, estudo) -> None:
        self.estudos.append(estudo)

    def remover_horario(self, estudo) -> None:
        if estudo in self.estudos:
            self.estudos.remove(estudo)

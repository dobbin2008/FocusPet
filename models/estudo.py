from datetime import datetime
from .database import db


class Estudo(db.Model):
    __tablename__ = "estudos"

    id = db.Column(db.Integer, primary_key=True)
    inicio = db.Column(db.DateTime, nullable=True)
    fim = db.Column(db.DateTime, nullable=True)
    duracao_minutos = db.Column(db.Integer, default=0)
    concluido = db.Column(db.Boolean, default=False)
    agenda_id = db.Column(db.Integer, db.ForeignKey("agendas.id"), nullable=False)

    agenda = db.relationship("Agenda", back_populates="estudos")

    def marcar_como_concluido(self) -> int:
        self.concluido = True
        return self.calcular_xp_para_pet()

    def calcular_xp_para_pet(self) -> int:
        if not self.concluido:
            return 0
        return max(10, int(self.duracao_minutos * 1.5))

    def enviar_notificacao(self) -> None:
        pass

    def gerar_estudo(self) -> "Estudo":
        return self

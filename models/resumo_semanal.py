from datetime import datetime
from .database import db


class ResumoSemanal(db.Model):
    __tablename__ = "resumos_semanais"

    id = db.Column(db.Integer, primary_key=True)
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)
    horas_estudadas = db.Column(db.Float, default=0.0)
    vezes_distraido = db.Column(db.Integer, default=0)
    progresso_pet = db.Column(db.Float, default=0.0)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

    estudante = db.relationship("Estudante", back_populates="resumos")

    def gerar_estatisticas(self, horas_estudadas: float, vezes_distraido: int) -> None:
        self.horas_estudadas = horas_estudadas
        self.vezes_distraido = vezes_distraido
        self.progresso_pet = self.calcular_tempo_total()

    def calcular_tempo_total(self) -> float:
        return self.horas_estudadas + self.vezes_distraido * 0.1

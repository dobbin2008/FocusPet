from backend.extensions import db
from backend.models.base import CrudModel


class ResumoSemanal(CrudModel, db.Model):
    __tablename__ = "resumos_semanais"

    data_inicio = db.Column(db.DateTime)
    data_fim = db.Column(db.DateTime)
    horas_estudadas = db.Column(db.Float, default=0)
    vezes_distraido = db.Column(db.Integer, default=0)
    progresso_pet = db.Column(db.Float, default=0)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)
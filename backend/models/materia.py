from backend.extensions import db
from backend.models.base import CrudModel


class Materia(CrudModel, db.Model):
    __tablename__ = "materias"

    nome = db.Column(db.String(80), nullable=False)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

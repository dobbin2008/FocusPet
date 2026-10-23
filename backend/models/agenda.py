from backend.extensions import db
from backend.models.base import CrudModel


class Agenda(CrudModel, db.Model):
    __tablename__ = "agendas"

    data_atual = db.Column(db.DateTime)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False, unique=True)
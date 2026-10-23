from backend.extensions import db
from backend.models.base import CrudModel


class ListaBloqueada(CrudModel, db.Model):
    __tablename__ = "listas_bloqueadas"

    url = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255))
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)
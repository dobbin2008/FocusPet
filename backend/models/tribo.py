from backend.extensions import db
from backend.models.base import CrudModel


class Tribo(CrudModel, db.Model):
    __tablename__ = "tribos"

    materia = db.Column(db.String(120), nullable=False)
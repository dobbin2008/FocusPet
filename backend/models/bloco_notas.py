from backend.extensions import db
from backend.models.base import CrudModel


class BlocoNotas(CrudModel, db.Model):
    __tablename__ = "blocos_de_notas"

    conteudo = db.Column(db.Text)
    hotkey = db.Column(db.String(20))
    notas_migradas = db.Column(db.Boolean, default=False, nullable=False)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False, unique=True)

    @classmethod
    def buscar_por_estudante(cls, estudante_id):
        return cls.query.filter_by(estudante_id=estudante_id).first()


class Nota(CrudModel, db.Model):
    __tablename__ = "notas"

    titulo = db.Column(db.String(120), nullable=False)
    conteudo = db.Column(db.Text, nullable=False, default="")
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False, index=True)
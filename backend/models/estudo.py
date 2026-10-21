from backend.extensions import db
from backend.models.base import CrudModel


class Estudo(CrudModel, db.Model):
    __tablename__ = "estudos"

    titulo = db.Column(db.String(200), nullable=False, default="Estudo")
    inicio = db.Column(db.DateTime)
    fim = db.Column(db.DateTime)
    duracao_minutos = db.Column(db.Integer, default=0)
    concluido = db.Column(db.Boolean, default=False)
    xp_ganho = db.Column(db.Integer, default=0, nullable=False)
    lembrete_em = db.Column(db.DateTime)
    lembrete_notificado = db.Column(db.Boolean, nullable=False, default=False)
    agenda_id = db.Column(db.Integer, db.ForeignKey("agendas.id"), nullable=False)
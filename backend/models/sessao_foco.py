from datetime import datetime, timezone

from backend.extensions import db
from backend.models.base import CrudModel


class SessaoFoco(CrudModel, db.Model):
    __tablename__ = "sessoes_de_foco"

    inicio = db.Column(db.DateTime)
    fim = db.Column(db.DateTime)
    modo_ativo = db.Column(db.Boolean, default=False)
    vezes_distraido = db.Column(db.Integer, default=0)
    tempo_total_minutos = db.Column(db.Integer, default=0)
    xp_ganho = db.Column(db.Integer, default=0)
    xp_bonus_meta = db.Column(db.Integer, nullable=False, default=0)
    token_api = db.Column(db.String(64), unique=True)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)
    materia_id = db.Column(
        db.Integer, db.ForeignKey("materias.id", ondelete="SET NULL"), nullable=True
    )
    materia = db.relationship("Materia")

    @property
    def minutos_estudados(self):
        if not self.modo_ativo:
            return self.tempo_total_minutos or 0
        if self.inicio is None:
            return 0

        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        inicio = self.inicio.replace(tzinfo=None) if self.inicio.tzinfo else self.inicio
        return max(0, int((agora - inicio).total_seconds() / 60))
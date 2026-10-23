from backend.extensions import db
from backend.models.base import CrudModel


class MetaEstudo(CrudModel, db.Model):
    __tablename__ = "metas_de_estudo"

    estudante_id = db.Column(
        db.Integer, db.ForeignKey("estudantes.id"), nullable=False, unique=True
    )
    meta_diaria_minutos = db.Column(db.Integer, nullable=False, default=0)
    meta_semanal_minutos = db.Column(db.Integer, nullable=False, default=0)
    meta_semanal_dias = db.Column(db.Integer, nullable=False, default=0)


class BonusMeta(CrudModel, db.Model):
    __tablename__ = "bonus_metas"
    __table_args__ = (
        db.UniqueConstraint(
            "estudante_id", "tipo", "periodo_inicio", name="uq_bonus_meta_periodo"
        ),
    )

    estudante_id = db.Column(
        db.Integer, db.ForeignKey("estudantes.id"), nullable=False
    )
    tipo = db.Column(db.String(10), nullable=False)
    periodo_inicio = db.Column(db.Date, nullable=False)
    xp_ganho = db.Column(db.Integer, nullable=False)

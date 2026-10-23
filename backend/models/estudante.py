from backend.extensions import db
from backend.models.base import CrudModel


class Estudante(CrudModel, db.Model):
    __tablename__ = "estudantes"

    email = db.Column(db.String(120), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    nome_exibicao = db.Column(db.String(120))
    foto_perfil = db.Column(db.String(255))
    xp_total = db.Column(db.Integer, default=0)
    tema_de_cores = db.Column(db.String(50), default="default")
    meta_diaria_minutos = db.Column(db.Integer, default=0)
    assinatura = db.Column(db.Boolean, default=False)
    pet_equipado_id = db.Column(db.Integer, db.ForeignKey("pets.id", ondelete="SET NULL", use_alter=True))

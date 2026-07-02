import datetime
from .database import db


class Estudante(db.Model):
    __tablename__ = "estudantes"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    xp_total = db.Column(db.Integer, default=0)
    tema_de_cores = db.Column(db.String(50), default="default")
    meta_diaria_minutos = db.Column(db.Integer, default=0)
    assinatura = db.Column(db.Boolean, default=False)
    tribo_id = db.Column(db.Integer, db.ForeignKey("tribos.id"), nullable=True)
    pet_equipado_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=True)

    agenda = db.relationship(
        "Agenda",
        uselist=False,
        back_populates="estudante",
        cascade="all, delete-orphan",
    )
    pets = db.relationship(
        "Pet",
        back_populates="dono",
        foreign_keys="Pet.estudante_id",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    pet_equipado = db.relationship(
        "Pet",
        foreign_keys=[pet_equipado_id],
        post_update=True,
        lazy="select",
    )
    notas = db.relationship(
        "BlocoDeNotas",
        back_populates="estudante",
        cascade="all, delete-orphan",
    )
    sessoes = db.relationship(
        "SessaoFoco",
        back_populates="estudante",
        cascade="all, delete-orphan",
    )
    resumos = db.relationship(
        "ResumoSemanal",
        back_populates="estudante",
        cascade="all, delete-orphan",
    )

    def cadastrar(self):
        self.data_criacao = datetime.datetime.utcnow()

    def login(self):
        return True

    def logout(self):
        return True

    def adicionar_xp(self, quantidade: int) -> None:
        self.xp_total = max(0, self.xp_total + quantidade)

    def equipar_pet(self, pet) -> None:
        if pet is not None and pet.estudante_id == self.id:
            self.pet_equipado = pet

    def ganhar_xp_ao_pet(self, quantidade: int) -> None:
        if self.pet_equipado is not None:
            self.pet_equipado.ganhar_xp(quantidade)

    def definir_meta_diaria(self, minutos: int) -> None:
        self.meta_diaria_minutos = minutos



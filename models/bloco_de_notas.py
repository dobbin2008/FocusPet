from .database import db


class BlocoDeNotas(db.Model):
    __tablename__ = "blocos_de_notas"

    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=True)
    hotkey = db.Column(db.String(20), nullable=True)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

    estudante = db.relationship("Estudante", back_populates="notas")

    def cadastrar_anotacao(self, texto: str) -> None:
        self.conteudo = texto

    def editar_anotacao(self, texto: str) -> None:
        self.conteudo = texto

    def excluir_anotacao(self) -> None:
        self.conteudo = ""

    def definir_hotkey(self, tecla: str) -> None:
        self.hotkey = tecla

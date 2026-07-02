import json
from datetime import datetime
from .database import db


class SessaoFoco(db.Model):
    __tablename__ = "sessoes_de_foco"

    id = db.Column(db.Integer, primary_key=True)
    inicio = db.Column(db.DateTime, nullable=True)
    fim = db.Column(db.DateTime, nullable=True)
    modo_ativo = db.Column(db.Boolean, default=False)
    sites_bloqueados = db.Column(db.Text, default="[]")
    vezes_distraido = db.Column(db.Integer, default=0)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

    estudante = db.relationship("Estudante", back_populates="sessoes")

    def iniciar_modo_foco(self) -> None:
        self.inicio = datetime.utcnow()
        self.modo_ativo = True

    def desativar_modo_foco(self) -> None:
        self.fim = datetime.utcnow()
        self.modo_ativo = False

    def adicionar_site_bloqueado(self, url: str) -> None:
        sites = self._carregar_sites()
        if url not in sites:
            sites.append(url)
            self.sites_bloqueados = json.dumps(sites)

    def remover_site_bloqueado(self, url: str) -> None:
        sites = self._carregar_sites()
        if url in sites:
            sites.remove(url)
            self.sites_bloqueados = json.dumps(sites)

    def registrar_distraicao(self) -> None:
        self.vezes_distraido += 1

    def calcular_xp_sessao(self) -> int:
        if not self.inicio or not self.fim:
            return 0
        duracao = self.fim - self.inicio
        minutos = int(duracao.total_seconds() / 60)
        return max(0, minutos * 2)

    def calcular_penalidade(self) -> int:
        return self.vezes_distraido * 5

    def xp_ganho(self) -> int:
        return max(0, self.calcular_xp_sessao() - self.calcular_penalidade())

    def aplicar_xp_ao_pet(self, pet) -> int:
        xp = self.xp_ganho()
        if pet is not None:
            pet.ganhar_xp(xp)
        return xp

    def _carregar_sites(self):
        try:
            return json.loads(self.sites_bloqueados or "[]")
        except ValueError:
            return []

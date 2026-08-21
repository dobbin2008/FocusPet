import json
from datetime import datetime
from .database import db


class SessaoFoco(db.Model):
    __tablename__ = "sessoes_de_foco"

    id = db.Column(db.Integer, primary_key=True)
    inicio = db.Column(db.DateTime, nullable=True)
    fim = db.Column(db.DateTime, nullable=True)
    modo_ativo = db.Column(db.Boolean, default=False)
    vezes_distraido = db.Column(db.Integer, default=0)
    tempo_total_minutos = db.Column(db.Integer, default=0)
    xp_ganho = db.Column(db.Integer, default=0)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

    estudante = db.relationship("Estudante", back_populates="sessoes")

    def iniciar_modo_foco(self) -> None:
        """Inicia uma sessão de modo foco."""
        self.inicio = datetime.utcnow()
        self.modo_ativo = True
        self.vezes_distraido = 0

    def desativar_modo_foco(self) -> None:
        """Encerra a sessão de modo foco."""
        self.fim = datetime.utcnow()
        self.modo_ativo = False
        self.calcular_tempo_total()
        self.xp_ganho = self.calcular_xp_sessao()

    def registrar_distraicao(self) -> None:
        """Registra uma tentativa de acesso a site bloqueado."""
        self.vezes_distraido += 1

    def calcular_tempo_total(self) -> None:
        """Calcula o tempo total da sessão em minutos."""
        if self.inicio and self.fim:
            duracao = self.fim - self.inicio
            self.tempo_total_minutos = int(duracao.total_seconds() / 60)

    def calcular_xp_sessao(self) -> int:
        """Calcula XP ganho na sessão (2 XP por minuto)."""
        if not self.inicio or not self.fim:
            return 0
        duracao = self.fim - self.inicio
        minutos = int(duracao.total_seconds() / 60)
        # XP base: 2 pontos por minuto
        xp_base = max(0, minutos * 2)
        # Aplicar penalidade por distrações
        penalidade = self.vezes_distraido * 5
        return max(0, xp_base - penalidade)

    def calcular_penalidade(self) -> int:
        """Calcula a penalidade total por distrações."""
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

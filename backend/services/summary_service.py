from datetime import datetime, time, timedelta, timezone

from backend.repositories.summary_repository import SummaryRepository
from backend.repositories.dashboard_repository import DashboardRepository


class GerarResumoSemanalService:
    def __init__(self, repository=None, dashboard_repository=None):
        self.repository = repository or SummaryRepository()
        self.dashboard_repository = dashboard_repository or DashboardRepository()

    def execute(self, estudante_id):
        estudante = self.dashboard_repository.buscar_estudante(estudante_id)
        if estudante is None:
            raise LookupError("Estudante não encontrado")
        hoje = datetime.now(timezone.utc).date()
        inicio_data = hoje - timedelta(days=hoje.weekday())
        inicio = datetime.combine(inicio_data, time.min)
        fim = inicio + timedelta(days=7)
        pet = self.dashboard_repository.buscar_pet_equipado(estudante_id)
        resumo, xp_ganho = self.repository.gerar(
            estudante_id,
            inicio,
            fim,
            pet.xp_atual if pet and pet.xp_atual else 0,
        )
        return {
            "inicio": resumo.data_inicio.date().isoformat(),
            "fim": resumo.data_fim.date().isoformat(),
            "horas_estudadas": resumo.horas_estudadas,
            "vezes_distraido": resumo.vezes_distraido,
            "progresso_pet": resumo.progresso_pet,
            "xp_ganho": xp_ganho,
        }
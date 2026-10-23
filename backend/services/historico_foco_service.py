from datetime import date, datetime, time, timedelta

from backend.repositories.focus_repository import FocusRepository


def _dados_sessao(sessao):
    return {
        "id": sessao.id,
        "inicio": sessao.inicio.isoformat() if sessao.inicio else None,
        "fim": sessao.fim.isoformat() if sessao.fim else None,
        "duracao_minutos": sessao.tempo_total_minutos or 0,
        "vezes_distraido": sessao.vezes_distraido or 0,
        "xp_ganho": sessao.xp_ganho or 0,
        "xp_bonus_meta": sessao.xp_bonus_meta or 0,
        "xp_base": max(0, (sessao.xp_ganho or 0) - (sessao.xp_bonus_meta or 0)),
        "materia": sessao.materia.nome if sessao.materia else None,
    }


class ListarHistoricoFocoService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, estudante_id, inicio=None, fim=None):
        data_inicio = self._parse_data(inicio, "início")
        data_fim = self._parse_data(fim, "fim")
        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValueError("A data inicial não pode ser posterior à data final.")

        inicio_datetime = (
            datetime.combine(data_inicio, time.min) if data_inicio else None
        )
        fim_exclusivo = (
            datetime.combine(data_fim + timedelta(days=1), time.min)
            if data_fim
            else None
        )
        sessoes = self.repository.listar_sessoes_concluidas(
            estudante_id, inicio_datetime, fim_exclusivo
        )
        return [_dados_sessao(sessao) for sessao in sessoes]

    @staticmethod
    def _parse_data(valor, nome):
        if valor in (None, ""):
            return None
        try:
            return date.fromisoformat(valor)
        except (TypeError, ValueError) as erro:
            raise ValueError(f"A data de {nome} deve estar no formato AAAA-MM-DD.") from erro


class ConsultarDetalheSessaoFocoService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, estudante_id, sessao_id):
        sessao = self.repository.buscar_sessao_concluida(estudante_id, sessao_id)
        if sessao is None:
            raise LookupError("Sessão concluída não encontrada.")
        return _dados_sessao(sessao)

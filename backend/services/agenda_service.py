from datetime import datetime, timezone

from backend.repositories.agenda_repository import AgendaRepository
from backend.xp import calcular_xp_atividade


def _dados_estudo(estudo):
    return {
        "id": estudo.id,
        "titulo": estudo.titulo,
        "data": estudo.inicio.strftime("%Y-%m-%d") if estudo.inicio else None,
        "duracao_minutos": estudo.duracao_minutos or 0,
        "lembrete_em": (
            estudo.lembrete_em.replace(tzinfo=timezone.utc).isoformat()
            if estudo.lembrete_em
            else None
        ),
        "concluido": bool(estudo.concluido),
        "xp": (
            estudo.xp_ganho
            if estudo.concluido
            else calcular_xp_atividade(estudo.duracao_minutos)
        ),
    }

def _validar_dados_atividade(dados, permitir_data_passada=False):
    titulo = str(dados.get("titulo", "")).strip()
    valor_data = str(dados.get("data", "")).strip()
    if not titulo or not valor_data:
        raise ValueError("Atividade e data são obrigatórias")
    try:
        data = datetime.strptime(valor_data, "%Y-%m-%d").date()
        duracao = int(dados.get("duracao_minutos", 30))
    except (TypeError, ValueError) as erro:
        raise ValueError("Data ou duração inválida") from erro
    if not permitir_data_passada and data < datetime.now().date():
        raise ValueError("Não é possível criar atividades em dias que já passaram.")
    if duracao < 0 or duracao > 1440:
        raise ValueError("A duração deve estar entre 0 e 1440 minutos")
    lembrete_em = None
    valor_lembrete = dados.get("lembrete_em")
    if valor_lembrete not in (None, ""):
        if not isinstance(valor_lembrete, str):
            raise ValueError("Data e hora do lembrete inválidas.")
        try:
            lembrete_em = datetime.fromisoformat(valor_lembrete)
            if lembrete_em.tzinfo is None:
                raise ValueError
            lembrete_em = lembrete_em.astimezone(timezone.utc).replace(tzinfo=None)
        except (TypeError, ValueError) as erro:
            raise ValueError("Data e hora do lembrete inválidas.") from erro
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        if lembrete_em <= agora:
            raise ValueError("O lembrete precisa estar em uma data e hora futuras.")
    return titulo[:200], data, duracao, lembrete_em


class ListarAtividadesService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id):
        return [_dados_estudo(estudo) for estudo in self.repository.listar_atividades(estudante_id)]


class CriarAtividadeService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id, dados):
        titulo, data, duracao, lembrete_em = _validar_dados_atividade(dados)
        estudo = self.repository.criar_atividade(
            estudante_id, titulo, data, duracao, lembrete_em
        )
        return _dados_estudo(estudo)

class EditarAtividadeService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id, estudo_id, dados):
        titulo, data, duracao, lembrete_em = _validar_dados_atividade(
            dados, permitir_data_passada=True
        )
        estudo = self.repository.atualizar_atividade_pendente(
            estudante_id, estudo_id, titulo, data, duracao, lembrete_em
        )
        if estudo is None:
            raise LookupError("Atividade pendente não encontrada")
        return _dados_estudo(estudo)


class ExcluirAtividadeService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id, estudo_id):
        if not self.repository.arquivar_atividade(estudante_id, estudo_id):
            raise LookupError("Atividade não encontrada")
        return {"sucesso": True}


class ListarLembretesVencidosService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        return [
            {
                "id": estudo.id,
                "titulo": estudo.titulo,
                "lembrete_em": estudo.lembrete_em.replace(
                    tzinfo=timezone.utc
                ).isoformat(),
            }
            for estudo in self.repository.listar_lembretes_vencidos(
                estudante_id, agora
            )
        ]


class ConfirmarLembreteEnviadoService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id, estudo_id):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.repository.marcar_lembrete_notificado(
            estudante_id, estudo_id, agora
        )


class ConcluirAtividadeService:
    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id, estudo_id):
        estudo = self.repository.buscar_atividade_do_estudante(estudante_id, estudo_id)
        if estudo is None:
            raise LookupError("Atividade não encontrada")
        if estudo.concluido:
            return {"sucesso": True, "xp_ganho": 0, "ja_concluido": True}
        xp_ganho = calcular_xp_atividade(estudo.duracao_minutos)
        if not self.repository.concluir_com_xp(estudante_id, estudo_id, xp_ganho):
            return {"sucesso": True, "xp_ganho": 0, "ja_concluido": True}
        estudo.concluido = True
        return {"sucesso": True, "xp_ganho": xp_ganho, "atividade": _dados_estudo(estudo)}
from datetime import datetime, timezone
import secrets

from backend.repositories.focus_repository import FocusRepository
from backend.services.metas_service import CalcularBonusMetaService
from backend.xp import calcular_xp_foco


class IniciarModoFocoService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, estudante_id, materia_id=None):
        sessao_ativa = self.repository.buscar_sessao_ativa(estudante_id)
        if sessao_ativa is not None:
            return sessao_ativa, False
        if materia_id is not None and not self.repository.materia_pertence_ao_estudante(
            estudante_id, materia_id
        ):
            raise ValueError("A matéria selecionada não foi encontrada.")
        sessao = self.repository.criar_sessao(
            estudante_id,
            datetime.now(timezone.utc).replace(tzinfo=None),
            secrets.token_urlsafe(32),
            materia_id,
        )
        return sessao, True


class ObterSessaoFocoAtivaService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, estudante_id):
        return self.repository.buscar_sessao_ativa(estudante_id)


class ConsultarSessaoFocoService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, estudante_id, sessao_id):
        sessao = self.repository.buscar_sessao_do_estudante(estudante_id, sessao_id)
        if sessao is None:
            raise LookupError("Sessão não encontrada")
        return sessao


class EncerrarModoFocoService:
    def __init__(self, repository=None, bonus_meta_service=None):
        self.repository = repository or FocusRepository()
        self.bonus_meta_service = bonus_meta_service or CalcularBonusMetaService()

    def execute(self, estudante_id, sessao_id):
        sessao = self.repository.buscar_sessao_do_estudante(estudante_id, sessao_id)
        if sessao is None:
            raise LookupError("Sessão não encontrada")
        if not sessao.modo_ativo:
            sessao.xp_ganho = 0
            sessao.xp_bonus_meta = 0
            sessao.ja_concluida = True
            return sessao
        fim = datetime.now(timezone.utc).replace(tzinfo=None)
        inicio = sessao.inicio
        if inicio.tzinfo is not None:
            inicio = inicio.replace(tzinfo=None)
        minutos = max(0, int((fim - inicio).total_seconds() / 60))
        xp_base = calcular_xp_foco(minutos, sessao.vezes_distraido)
        bonus_periodos = self.bonus_meta_service.execute(estudante_id, fim, minutos)
        xp_bonus_meta = sum(bonus["xp_ganho"] for bonus in bonus_periodos)
        xp_ganho = xp_base + xp_bonus_meta
        if not self.repository.encerrar_com_xp(
            estudante_id, sessao_id, fim, minutos, xp_ganho, bonus_periodos
        ):
            sessao = self.repository.buscar_sessao_do_estudante(estudante_id, sessao_id)
            sessao.xp_ganho = 0
            sessao.ja_concluida = True
            return sessao
        sessao.fim = fim
        sessao.modo_ativo = False
        sessao.tempo_total_minutos = minutos
        sessao.xp_ganho = xp_ganho
        sessao.xp_bonus_meta = xp_bonus_meta
        sessao.ja_concluida = False
        return sessao


class RegistrarDistracaoService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, estudante_id, sessao_id):
        sessao = self.repository.registrar_distraicao(estudante_id, sessao_id)
        if sessao is None:
            raise LookupError("Sessão ativa não encontrada")
        return sessao


class ValidarTokenSessaoService:
    def __init__(self, repository=None):
        self.repository = repository or FocusRepository()

    def execute(self, sessao_id, token_api):
        if not token_api:
            return None
        return self.repository.buscar_por_token(sessao_id, token_api)
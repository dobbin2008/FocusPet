from datetime import datetime, time, timedelta, timezone

from backend.repositories.metas_repository import MetasRepository
from backend.xp import calcular_xp_bonus_meta


class ObterMetasEstudoService:
    def __init__(self, repository=None):
        self.repository = repository or MetasRepository()

    def execute(self, estudante_id):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        progresso = self.repository.progresso_atual(estudante_id, agora)
        meta = self.repository.obter(estudante_id)
        bonus = self.repository.listar_bonus(
            estudante_id,
            progresso["inicio_dia"],
            progresso["inicio_semana"],
        )
        bonus_por_tipo = {registro.tipo: registro.xp_ganho for registro in bonus}
        diaria = meta.meta_diaria_minutos if meta else 0
        semanal = meta.meta_semanal_minutos if meta else 0
        semanal_dias = meta.meta_semanal_dias if meta else 0
        semanal_atingido = (
            progresso["dias_semanais"] if semanal_dias else progresso["minutos_semanais"]
        )
        return {
            "meta_diaria_minutos": diaria,
            "meta_semanal_minutos": semanal,
            "meta_semanal_dias": semanal_dias,
            "diaria": self._dados_progresso(
                progresso["minutos_diarios"],
                diaria,
                bonus_por_tipo.get("diaria"),
            ),
            "semanal": self._dados_progresso(
                semanal_atingido,
                semanal,
                bonus_por_tipo.get("semanal"),
                meta_dias=semanal_dias,
            ),
            "inicio_dia": progresso["inicio_dia"].isoformat(),
            "inicio_semana": progresso["inicio_semana"].isoformat(),
        }

    @staticmethod
    def _dados_progresso(
        minutos, meta_minutos, bonus_concedido, meta_dias=0
    ):
        meta_valor = meta_dias or meta_minutos
        atingida = meta_valor > 0 and minutos >= meta_valor
        return {
            "minutos_estudados": minutos if not meta_dias else 0,
            "meta_minutos": meta_minutos if not meta_dias else 0,
            "dias_estudados": minutos if meta_dias else 0,
            "meta_dias": meta_dias,
            "percentual": (
                min(100, round(minutos * 100 / meta_valor))
                if meta_valor
                else 0
            ),
            "atingida": atingida,
            "bonus_xp": bonus_concedido or (
                min(20, meta_dias * 10)
                if meta_dias
                else calcular_xp_bonus_meta(meta_minutos) if meta_minutos else 0
            ),
            "bonus_concedido": bonus_concedido is not None,
        }


class ConfigurarMetasEstudoService:
    def __init__(self, repository=None):
        self.repository = repository or MetasRepository()

    def execute(self, estudante_id, dados):
        diaria = self._validar_valor_inteiro(
            dados.get("meta_diaria_minutos", 0), 1440, "diária"
        )
        semanal_dias = self._validar_valor_inteiro(
            dados.get("meta_semanal_dias", 0), 7, "semanal em dias"
        )
        semanal = self._validar_valor_inteiro(
            dados.get("meta_semanal_minutos", 0), 10080, "semanal"
        )
        if semanal and semanal_dias:
            raise ValueError("Escolha a meta semanal em horas ou em dias.")
        if diaria and (semanal or semanal_dias):
            raise ValueError("Configure uma meta diária ou uma meta semanal, não as duas ao mesmo tempo.")
        self.repository.salvar(estudante_id, diaria, semanal, semanal_dias)
        return ObterMetasEstudoService(self.repository).execute(estudante_id)

    @staticmethod
    def _validar_valor_inteiro(valor, maximo, nome):
        if isinstance(valor, bool):
            raise ValueError(f"A meta {nome} deve ser um número inteiro.")
        try:
            valor_inteiro = int(valor)
        except (OverflowError, TypeError, ValueError) as erro:
            raise ValueError(f"A meta {nome} deve ser um número inteiro.") from erro
        if valor_inteiro < 0 or valor_inteiro > maximo:
            raise ValueError(
                f"A meta {nome} deve ficar entre 0 e {maximo}."
            )
        if isinstance(valor, float) and not valor.is_integer():
            raise ValueError(f"A meta {nome} deve ser um número inteiro.")
        return valor_inteiro


class CalcularBonusMetaService:
    def __init__(self, repository=None):
        self.repository = repository or MetasRepository()

    def execute(self, estudante_id, fim_sessao, minutos_sessao):
        meta = self.repository.obter(estudante_id)
        if meta is None or minutos_sessao <= 0:
            return []

        inicio_dia = fim_sessao.date()
        inicio_semana = inicio_dia - timedelta(days=inicio_dia.weekday())
        periodos = (
            (
                "diaria",
                meta.meta_diaria_minutos,
                inicio_dia,
                datetime.combine(inicio_dia, time.min),
                datetime.combine(inicio_dia + timedelta(days=1), time.min),
            ),
            (
                "semanal",
                meta.meta_semanal_minutos,
                inicio_semana,
                datetime.combine(inicio_semana, time.min),
                datetime.combine(inicio_semana + timedelta(days=7), time.min),
            ),
        )
        bonus_devidos = []
        for tipo, meta_minutos, inicio_periodo, inicio, fim in periodos:
            if meta_minutos <= 0:
                continue
            minutos_anteriores = self.repository.minutos_foco_no_periodo(
                estudante_id, inicio, fim
            )
            if (
                minutos_anteriores < meta_minutos
                <= minutos_anteriores + minutos_sessao
                and not self.repository.bonus_ja_concedido(
                    estudante_id, tipo, inicio_periodo
                )
            ):
                bonus_devidos.append({
                    "tipo": tipo,
                    "periodo_inicio": inicio_periodo,
                    "xp_ganho": calcular_xp_bonus_meta(meta_minutos),
                })
        if meta.meta_semanal_dias > 0:
            inicio_semana = datetime.combine(
                inicio_dia - timedelta(days=inicio_dia.weekday()), time.min
            )
            fim_semana = inicio_semana + timedelta(days=7)
            dias_anteriores = self.repository.dias_foco_no_periodo(
                estudante_id, inicio_semana, fim_semana
            )
            dia_atual_ja_contado = self.repository.dias_foco_no_periodo(
                estudante_id,
                datetime.combine(inicio_dia, time.min),
                datetime.combine(inicio_dia + timedelta(days=1), time.min),
            )
            dias_apos_sessao = dias_anteriores + (0 if dia_atual_ja_contado else 1)
            if (
                dias_anteriores < meta.meta_semanal_dias <= dias_apos_sessao
                and not self.repository.bonus_ja_concedido(
                    estudante_id, "semanal", inicio_semana.date()
                )
            ):
                bonus_devidos.append({
                    "tipo": "semanal",
                    "periodo_inicio": inicio_semana.date(),
                    "xp_ganho": min(20, meta.meta_semanal_dias * 10),
                })
        return bonus_devidos

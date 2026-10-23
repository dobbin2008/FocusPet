from datetime import datetime, timezone
import math

from backend.repositories.agenda_repository import AgendaRepository
from backend.repositories.pet_repository import PetRepository
from backend.services.pet_service import serializar_pet


class SimularEstudoService:
    HORAS_MINIMAS = 0.5
    HORAS_MAXIMAS = 12

    def __init__(self, repository=None):
        self.repository = repository or AgendaRepository()

    def execute(self, estudante_id, horas):
        try:
            horas = float(horas)
        except (TypeError, ValueError) as erro:
            raise ValueError("Informe a duração do estudo em horas.") from erro
        if not math.isfinite(horas) or not self.HORAS_MINIMAS <= horas <= self.HORAS_MAXIMAS:
            raise ValueError("A duração deve estar entre 0,5 e 12 horas.")
        duracao_minutos = round(horas * 60)
        if duracao_minutos % 30:
            raise ValueError("Use intervalos de meia hora.")

        inicio = datetime.now(timezone.utc).replace(tzinfo=None)
        estudo, xp_ganho = self.repository.simular_estudo_concluido(
            estudante_id, duracao_minutos, inicio
        )
        return {
            "sucesso": True,
            "atividade": {
                "id": estudo.id,
                "titulo": estudo.titulo,
                "data": estudo.inicio.strftime("%Y-%m-%d"),
                "duracao_minutos": estudo.duracao_minutos,
                "concluido": True,
            },
            "horas_estudadas": duracao_minutos / 60,
            "xp_ganho": xp_ganho,
        }


class ResetarXpPetEquipadoService:
    def __init__(self, repository=None):
        self.repository = repository or PetRepository()

    def execute(self, estudante_id):
        resultado = self.repository.resetar_xp_pet_equipado(estudante_id)
        if resultado is None:
            raise LookupError("Não há pet equipado para resetar.")
        pet, xp_resetado = resultado
        return {
            "sucesso": True,
            "xp_resetado": xp_resetado,
            "pet": serializar_pet(pet),
        }

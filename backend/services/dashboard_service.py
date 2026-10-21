import re

from backend.repositories.dashboard_repository import DashboardRepository
from backend.services.pet_service import serializar_pet


def _nome_exibicao(estudante):
    nome = estudante.nome_exibicao or estudante.email.split("@", 1)[0]
    nome = re.sub(r"([a-z])([A-Z])", r"\1 \2", nome)
    nome = re.sub(r"[._-]+", " ", nome)
    return " ".join(parte.capitalize() for parte in nome.split()) or "Estudante"


def _iniciais(nome):
    partes = nome.split()
    if len(partes) > 1:
        return f"{partes[0][0]}{partes[-1][0]}".upper()
    return nome[:2].upper()


class ObterDashboardService:
    def __init__(self, repository=None):
        self.repository = repository or DashboardRepository()

    def execute(self, estudante_id):
        estudante = self.repository.buscar_estudante(estudante_id)
        if estudante is None:
            raise LookupError("Estudante não encontrado")
        pet = self.repository.buscar_pet_equipado(estudante_id)
        xp_total_pets = self.repository.xp_total_dos_pets(estudante_id)
        nome = _nome_exibicao(estudante)
        return {
            "estudante": {
                "nome": nome,
                "iniciais": _iniciais(nome),
                "email": estudante.email,
                "xp_total": xp_total_pets,
                "foto_url": "/api/perfil/foto" if estudante.foto_perfil else None,
            },
            "pet": None if pet is None else serializar_pet(pet),
        }
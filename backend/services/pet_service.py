from backend.repositories.pet_repository import PetRepository


def serializar_pet(pet):
    return {
        "id": pet.id,
        "nome": pet.nome_atual,
        "linha_evolutiva": pet.linha_evolutiva,
        "nivel": pet.nivel,
        "xp_atual": pet.xp_atual or 0,
        "xp_progresso_nivel": pet.xp_progresso_nivel,
        "xp_para_proximo_nivel": pet.xp_para_proximo_nivel,
        "proximo_nivel": pet.nivel + 1 if pet.nivel < pet.NIVEL_MAXIMO else None,
        "nivel_maximo": pet.NIVEL_MAXIMO,
        "imagem_url": pet.imagem_url,
        "evolucao": pet.evolucao,
    }


class ListarPetsDisponiveisService:
    def __init__(self, repository=None):
        self.repository = repository or PetRepository()

    def execute(self, estudante_id):
        return self.repository.listar_disponiveis(estudante_id)


class EquiparPetService:
    def __init__(self, repository=None):
        self.repository = repository or PetRepository()

    def execute(self, estudante_id, pet_id):
        try:
            pet_id = int(pet_id)
        except (TypeError, ValueError) as erro:
            raise ValueError("Pet inválido") from erro
        pet = self.repository.equipar(estudante_id, pet_id)
        if pet is None:
            raise LookupError("Pet indisponível")
        return pet


class ConcederXpTestePetService:
    XP_DE_TESTE = 100

    def __init__(self, repository=None):
        self.repository = repository or PetRepository()

    def execute(self, estudante_id):
        pet = self.repository.adicionar_xp_pet_equipado(estudante_id, self.XP_DE_TESTE)
        if pet is None:
            raise LookupError("Não há pet equipado para receber XP")
        return pet


class CriarPetsIniciaisService:
    def __init__(self, repository=None):
        self.repository = repository or PetRepository()

    def execute(self, estudante_id):
        return self.repository.criar_pets_iniciais_se_necessario(estudante_id)
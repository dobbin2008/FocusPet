from models import Pet, Tribo


def criar_pet(nome: str, nivel: int = 1) -> Pet:
    return Pet.criar(nome=nome, nivel=nivel)


def listar_pets():
    return Pet.listar_todos()


def deletar_pet(pet_id: int) -> None:
    Pet.deletar_por_id(pet_id)


def criar_tribo(materia: str) -> Tribo:
    return Tribo.criar(materia=materia)


def listar_tribos():
    return Tribo.listar_todos()


def deletar_tribo(tribo_id: int) -> None:
    Tribo.deletar_por_id(tribo_id)

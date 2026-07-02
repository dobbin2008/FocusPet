from models import Pet, Tribo, db


def criar_pet(nome: str, nivel: int = 1) -> Pet:
    pet = Pet(nome=nome, nivel=nivel)
    db.session.add(pet)
    db.session.commit()
    return pet


def listar_pets():
    return Pet.query.all()


def deletar_pet(pet_id: int) -> None:
    pet = Pet.query.get(pet_id)
    if pet:
        db.session.delete(pet)
        db.session.commit()


def criar_tribo(materia: str) -> Tribo:
    tribo = Tribo(materia=materia)
    db.session.add(tribo)
    db.session.commit()
    return tribo


def listar_tribos():
    return Tribo.query.all()


def deletar_tribo(tribo_id: int) -> None:
    tribo = Tribo.query.get(tribo_id)
    if tribo:
        db.session.delete(tribo)
        db.session.commit()

from models import Estudante


def cadastrar_estudante(email: str, senha: str) -> Estudante:
    return Estudante.criar(email=email, senha=senha)


def autenticar_estudante(email: str, senha: str):
    return Estudante.autenticar(email=email, senha=senha)


def listar_estudantes():
    return Estudante.listar_todos()

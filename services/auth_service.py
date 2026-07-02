from models import Estudante, db


def cadastrar_estudante(email: str, senha: str) -> Estudante:
    if not email or not senha:
        raise ValueError("Email e senha são obrigatórios")

    if Estudante.query.filter_by(email=email).first():
        raise ValueError("Este email já está cadastrado")

    estudante = Estudante(email=email, senha=senha)
    db.session.add(estudante)
    db.session.commit()
    return estudante


def autenticar_estudante(email: str, senha: str):
    return Estudante.query.filter_by(email=email, senha=senha).first()

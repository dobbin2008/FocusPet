from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models import Estudante
from backend.repositories.auth_repository import AuthRepository
from backend.services.perfil_service import remover_foto_perfil, salvar_foto_perfil


def validar_senha(senha):
    senha = str(senha or "")
    requisitos = (
        len(senha) >= 12,
        any(caractere.isupper() for caractere in senha),
        any(caractere.islower() for caractere in senha),
        any(caractere.isdigit() for caractere in senha),
        any(not caractere.isalnum() and not caractere.isspace() for caractere in senha),
    )
    if not all(requisitos):
        raise ValueError(
            "A senha precisa ter ao menos 12 caracteres, uma maiúscula, "
            "uma minúscula, um número e um símbolo especial."
        )


class CadastrarEstudanteService:
    def __init__(self, repository=None):
        self.repository = repository or AuthRepository()

    def execute(self, email, senha, nome_exibicao=None, foto_perfil=None, diretorio_fotos=None):
        email = str(email or "").strip().lower()
        senha = str(senha or "")
        if not email or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("Informe um email válido")
        validar_senha(senha)
        if self.repository.buscar_por_email(email):
            raise ValueError("Este email já está cadastrado")
        nome_exibicao = str(nome_exibicao or "").strip()[:120] or None
        if foto_perfil and not diretorio_fotos:
            raise ValueError("O armazenamento de fotos não está configurado")
        nome_foto = salvar_foto_perfil(foto_perfil, diretorio_fotos) if foto_perfil else None
        estudante = Estudante(
            email=email,
            senha=generate_password_hash(senha),
            nome_exibicao=nome_exibicao,
            foto_perfil=nome_foto,
        )
        try:
            return estudante.salvar()
        except IntegrityError as erro:
            self.repository.descartar_alteracoes()
            remover_foto_perfil(nome_foto, diretorio_fotos)
            raise ValueError("Este email já está cadastrado") from erro
        except Exception:
            self.repository.descartar_alteracoes()
            remover_foto_perfil(nome_foto, diretorio_fotos)
            raise


class AutenticarEstudanteService:
    def __init__(self, repository=None):
        self.repository = repository or AuthRepository()

    def execute(self, email, senha):
        estudante = self.repository.buscar_por_email(str(email or "").strip().lower())
        if estudante is None or not check_password_hash(estudante.senha, str(senha or "")):
            return None
        return estudante


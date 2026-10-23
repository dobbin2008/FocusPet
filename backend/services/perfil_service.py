from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db
from backend.models import Estudante
from backend.repositories.auth_repository import AuthRepository
from backend.services.validacoes import validar_senha


class EmailJaCadastradoError(Exception):
    pass


def salvar_foto_perfil(arquivo, diretorio):
    if arquivo is None or not getattr(arquivo, "filename", ""):
        return None
    pasta = Path(diretorio)
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid4().hex}.webp"
    destino = pasta / nome
    temporario = pasta / f"{nome}.tmp"
    try:
        with Image.open(arquivo.stream) as original:
            if original.format not in {"PNG", "JPEG", "WEBP"}:
                raise ValueError("Use uma imagem PNG, JPEG ou WebP")
            if original.width * original.height > 20_000_000:
                raise ValueError("A imagem tem dimensões muito grandes")
            imagem = ImageOps.exif_transpose(original)
            imagem.thumbnail((512, 512))
            if imagem.mode not in {"RGB", "RGBA"}:
                imagem = imagem.convert("RGBA" if "transparency" in imagem.info else "RGB")
            imagem.save(temporario, format="WEBP", quality=86, method=6)
        temporario.replace(destino)
        return nome
    except ValueError:
        temporario.unlink(missing_ok=True)
        raise
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as erro:
        temporario.unlink(missing_ok=True)
        raise ValueError("O arquivo enviado não é uma imagem válida") from erro


def remover_foto_perfil(nome, diretorio):
    if not nome or Path(nome).name != nome:
        return
    (Path(diretorio) / nome).unlink(missing_ok=True)


class ObterFotoPerfilService:
    def execute(self, estudante_id, diretorio):
        estudante = Estudante.buscar_por_id(estudante_id)
        if estudante is None:
            raise LookupError("Estudante não encontrado")
        nome = estudante.foto_perfil
        if not nome or Path(nome).name != nome:
            return None
        caminho = Path(diretorio) / nome
        return caminho if caminho.is_file() else None


class ObterPerfilService:
    def execute(self, estudante_id):
        estudante = Estudante.buscar_por_id(estudante_id)
        if estudante is None:
            raise LookupError("Estudante não encontrado")
        return {
            "nome": estudante.nome_exibicao or "",
            "email": estudante.email,
            "foto_url": "/api/perfil/foto" if estudante.foto_perfil else None,
        }


class AtualizarPerfilService:
    def __init__(self, auth_repository=None):
        self.auth_repository = auth_repository or AuthRepository()

    def execute(
        self,
        estudante_id,
        nome,
        arquivo_foto=None,
        remover_foto=False,
        diretorio=None,
        email=None,
        senha_atual=None,
        nova_senha=None,
        confirmar_senha=None,
    ):
        nome = str(nome or "").strip()
        if not nome:
            raise ValueError("Informe seu nome de usuário.")
        if len(nome) > 120:
            raise ValueError("O nome de usuário deve ter no máximo 120 caracteres.")
        estudante = Estudante.buscar_por_id(estudante_id)
        if estudante is None:
            raise LookupError("Estudante não encontrado")

        email = estudante.email if email is None else str(email).strip().lower()
        if (
            not email
            or len(email) > 120
            or "@" not in email
            or "." not in email.rsplit("@", 1)[-1]
        ):
            raise ValueError("Informe um email válido.")
        estudante_com_email = self.auth_repository.buscar_por_email(email)
        if estudante_com_email and estudante_com_email.id != estudante.id:
            raise EmailJaCadastradoError("Este email já está cadastrado.")

        senha_atual = str(senha_atual or "")
        nova_senha = str(nova_senha or "")
        confirmar_senha = str(confirmar_senha or "")
        atualizar_senha = bool(nova_senha or confirmar_senha)
        senha_atualizada = None
        if atualizar_senha:
            if not senha_atual:
                raise ValueError("Informe sua senha atual para definir uma nova senha.")
            if not check_password_hash(estudante.senha, senha_atual):
                raise ValueError("A senha atual está incorreta.")
            if not nova_senha:
                raise ValueError("Informe a nova senha.")
            validar_senha(nova_senha)
            if nova_senha != confirmar_senha:
                raise ValueError("A confirmação da nova senha não corresponde.")
            senha_atualizada = generate_password_hash(nova_senha)
        elif senha_atual:
            raise ValueError("Informe a nova senha e sua confirmação.")

        foto_antiga = estudante.foto_perfil
        arquivo_enviado = bool(arquivo_foto and getattr(arquivo_foto, "filename", ""))
        nova_foto = salvar_foto_perfil(arquivo_foto, diretorio) if arquivo_enviado else None
        foto_atualizada = nova_foto if arquivo_enviado else (
            None if remover_foto else foto_antiga
        )
        try:
            estudante.nome_exibicao = nome
            estudante.email = email
            estudante.foto_perfil = foto_atualizada
            if senha_atualizada:
                estudante.senha = senha_atualizada
            db.session.commit()
        except IntegrityError as erro:
            db.session.rollback()
            remover_foto_perfil(nova_foto, diretorio)
            raise EmailJaCadastradoError("Este email já está cadastrado.") from erro
        except SQLAlchemyError:
            db.session.rollback()
            remover_foto_perfil(nova_foto, diretorio)
            raise
        if foto_antiga and foto_antiga != estudante.foto_perfil:
            remover_foto_perfil(foto_antiga, diretorio)
        return {
            "nome": estudante.nome_exibicao,
            "email": estudante.email,
            "foto_url": "/api/perfil/foto" if estudante.foto_perfil else None,
        }
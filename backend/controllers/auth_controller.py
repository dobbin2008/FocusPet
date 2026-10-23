from functools import wraps
from pathlib import Path

from flask import Blueprint, current_app, jsonify, redirect, request, send_from_directory, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge

from backend.services.auth_service import AutenticarEstudanteService, CadastrarEstudanteService
from backend.services.captcha_service import TurnstileUnavailableError, ValidarTurnstileService

auth_bp = Blueprint("auth", __name__)
PAGES = Path(__file__).resolve().parents[2] / "frontend" / "pages"


def pagina_estatica(nome):
    return send_from_directory(PAGES, nome)


@auth_bp.errorhandler(RequestEntityTooLarge)
def upload_muito_grande(_erro):
    return jsonify({"erro": "A imagem deve ter no máximo 5 MB"}), 413


def _requisicao_api():
    return request.path.startswith("/api/")


def login_required(view_func):
    @wraps(view_func)
    def decorator(*args, **kwargs):
        if "user_id" not in session:
            if _requisicao_api():
                return jsonify({"erro": "Não autenticado"}), 401
            return redirect(url_for("auth.login_page"))
        return view_func(*args, **kwargs)

    return decorator


def developer_required(view_func):
    @wraps(view_func)
    def decorator(*args, **kwargs):
        email_configurado = str(current_app.config.get("DEVELOPER_EMAIL") or "").strip().lower()
        eh_desenvolvedor = (
            session.get("developer_mode") is True
            and email_configurado
            and session.get("email", "").strip().lower() == email_configurado
        )
        if not eh_desenvolvedor:
            if _requisicao_api():
                return jsonify({"erro": "Acesso restrito ao desenvolvedor"}), 403
            return redirect(url_for("main.index"))
        return view_func(*args, **kwargs)

    return decorator


class AuthController:
    def __init__(self, cadastrar_service=None, autenticar_service=None, turnstile_service=None):
        self.cadastrar_service = cadastrar_service or CadastrarEstudanteService()
        self.autenticar_service = autenticar_service or AutenticarEstudanteService()
        self.turnstile_service = turnstile_service or ValidarTurnstileService()

    def login_page(self):
        return pagina_estatica("login.html")

    def cadastro_page(self):
        return pagina_estatica("cadastro.html")

    def captcha_config(self):
        return jsonify({"site_key": current_app.config.get("TURNSTILE_SITE_KEY", "")})

    @login_required
    def sessao_atual(self):
        return jsonify({"sucesso": True, "is_developer": session.get("developer_mode") is True})

    def cadastrar(self):
        dados = request.get_json(silent=True) if request.is_json else request.form
        dados = dados or {}
        try:
            captcha_valido = self.turnstile_service.execute(
                dados.get("cf-turnstile-response"), request.remote_addr
            )
        except TurnstileUnavailableError:
            return jsonify({"erro": "Verificação antirobô indisponível. Configure o CAPTCHA e tente novamente."}), 503
        if not captcha_valido:
            return jsonify({"erro": "Conclua a verificação antirobô para criar sua conta."}), 400
        try:
            estudante = self.cadastrar_service.execute(
                dados.get("email"),
                dados.get("senha"),
                dados.get("nome"),
                request.files.get("foto_perfil"),
                current_app.config["PROFILE_UPLOAD_FOLDER"],
            )
            return jsonify({
                "sucesso": True,
                "email": estudante.email,
                "nome": estudante.nome_exibicao,
                "foto_perfil": bool(estudante.foto_perfil),
            }), 201
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

    def login(self):
        dados = request.get_json(silent=True) or {}
        estudante = self.autenticar_service.execute(dados.get("email"), dados.get("senha"))
        if estudante is None:
            return jsonify({"erro": "Email ou senha inválidos"}), 401
        session.clear()
        session.permanent = True
        session["user_id"] = estudante.id
        session["email"] = estudante.email
        email_desenvolvedor = str(current_app.config.get("DEVELOPER_EMAIL") or "").strip().lower()
        eh_desenvolvedor = bool(email_desenvolvedor) and estudante.email.strip().lower() == email_desenvolvedor
        session["developer_mode"] = eh_desenvolvedor
        return jsonify({
            "sucesso": True,
            "is_developer": eh_desenvolvedor,
            "destino": "/desenvolvedor" if eh_desenvolvedor else "/",
        })

    def logout(self):
        session.clear()
        return jsonify({"sucesso": True})


auth_controller = AuthController()
auth_bp.add_url_rule("/login", view_func=auth_controller.login_page, methods=["GET"])
auth_bp.add_url_rule("/cadastro", view_func=auth_controller.cadastro_page, methods=["GET"])
auth_bp.add_url_rule("/api/auth/captcha-config", view_func=auth_controller.captcha_config, methods=["GET"])
auth_bp.add_url_rule("/api/auth/session", view_func=auth_controller.sessao_atual, methods=["GET"])
auth_bp.add_url_rule("/api/auth/cadastro", view_func=auth_controller.cadastrar, methods=["POST"])
auth_bp.add_url_rule("/api/auth/login", view_func=auth_controller.login, methods=["POST"])
auth_bp.add_url_rule("/api/auth/logout", view_func=auth_controller.logout, methods=["POST"])
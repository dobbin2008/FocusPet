import os

from flask import Blueprint, redirect, request, send_from_directory, session, url_for

from services.auth_service import AutenticarEstudanteService, CadastrarEstudanteService

auth_bp = Blueprint("auth", __name__, url_prefix="")


def pagina_estatica(nome):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"), nome)


def login_required(view_func):
    def decorator(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    decorator.__name__ = view_func.__name__
    return decorator


class AuthController:
    def __init__(self, cadastrar_service=None, autenticar_service=None):
        self.cadastrar_service = cadastrar_service or CadastrarEstudanteService()
        self.autenticar_service = autenticar_service or AutenticarEstudanteService()

    def cadastro(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")
            try:
                self.cadastrar_service.execute(email, senha)
                return redirect(url_for("auth.login"))
            except ValueError as exc:
                return f"Erro: {exc}", 400

        return pagina_estatica("cadastro.html")

    def login(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")
            destino = request.form.get("next", "site")
            estudante = self.autenticar_service.execute(email, senha)
            if estudante is not None:
                session.permanent = True
                session["user_id"] = estudante.id
                session["email"] = estudante.email
                if destino == "admin":
                    return redirect(url_for("admin.painel_admin"))
                return redirect(url_for("main.index"))
            return "Credenciais inválidas", 401

        if "user_id" in session:
            return redirect(url_for("main.index"))

        return pagina_estatica("login.html")

    @login_required
    def logout(self):
        session.clear()
        return redirect(url_for("auth.login"))


auth_controller = AuthController()
auth_bp.add_url_rule("/cadastro", view_func=auth_controller.cadastro, methods=["GET", "POST"])
auth_bp.add_url_rule("/login", view_func=auth_controller.login, methods=["GET", "POST"])
auth_bp.add_url_rule("/logout", view_func=auth_controller.logout)

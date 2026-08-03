from flask import Blueprint, redirect, render_template, request, session, url_for

from services.auth_service import autenticar_estudante, cadastrar_estudante

auth_bp = Blueprint("auth", __name__, url_prefix="")


def login_required(view_func):
    def decorator(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    decorator.__name__ = view_func.__name__
    return decorator


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        try:
            cadastrar_estudante(email, senha)
            return redirect(url_for("auth.login"))
        except ValueError as exc:
            return f"Erro: {exc}", 400

    return render_template("cadastro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        destino = request.form.get("next", "site")
        estudante = autenticar_estudante(email, senha)
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

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

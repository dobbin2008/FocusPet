from flask import Blueprint, redirect, render_template, request, url_for

from models import Estudante, Pet, Tribo
from services.admin_service import (
    criar_pet,
    criar_tribo,
    deletar_pet,
    deletar_tribo,
    listar_pets,
    listar_tribos,
)
from services.auth_service import cadastrar_estudante
from .auth_controller import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def painel_admin():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "criar_estudante":
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")
            try:
                cadastrar_estudante(email, senha)
            except ValueError:
                pass

        elif action == "criar_pet":
            nome = request.form.get("nome", "").strip()
            if nome:
                criar_pet(nome)

        elif action == "criar_tribo":
            materia = request.form.get("materia", "").strip()
            if materia:
                criar_tribo(materia)

    estudantes = Estudante.query.all()
    pets = listar_pets()
    tribos = listar_tribos()
    return render_template("admin.html", estudantes=estudantes, pets=pets, tribos=tribos)


@admin_bp.route("/pets/<int:pet_id>/delete", methods=["POST"])
@login_required
def deletar_pet_admin(pet_id):
    deletar_pet(pet_id)
    return redirect(url_for("admin.painel_admin"))


@admin_bp.route("/tribos/<int:tribo_id>/delete", methods=["POST"])
@login_required
def deletar_tribo_admin(tribo_id):
    deletar_tribo(tribo_id)
    return redirect(url_for("admin.painel_admin"))
